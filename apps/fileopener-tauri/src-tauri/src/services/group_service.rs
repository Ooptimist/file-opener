use std::collections::{BTreeMap, HashSet};
use std::fs;
use std::path::{Component, Path, PathBuf};
use std::process::Command;

use tauri::{AppHandle, Manager};

pub type Groups = BTreeMap<String, Vec<String>>;

const GROUPS_FILE_NAME: &str = "file_groups.json";

#[derive(serde::Serialize)]
pub struct ExportGroupsResult {
    #[serde(rename = "groupCount")]
    pub group_count: u32,
    #[serde(rename = "fileCount")]
    pub file_count: u32,
    pub path: String,
}

#[derive(serde::Serialize)]
pub struct ImportGroupsResult {
    #[serde(rename = "groupCount")]
    pub group_count: u32,
    #[serde(rename = "fileCount")]
    pub file_count: u32,
    #[serde(rename = "skippedGroups")]
    pub skipped_groups: u32,
    pub path: String,
}

#[derive(serde::Serialize)]
pub struct GroupHealthItem {
    pub name: String,
    pub existing: u32,
    pub total: u32,
    #[serde(rename = "missingFiles")]
    pub missing_files: Vec<String>,
}

#[derive(serde::Serialize)]
pub struct GroupHealthReport {
    #[serde(rename = "groupCount")]
    pub group_count: u32,
    #[serde(rename = "fileCount")]
    pub file_count: u32,
    #[serde(rename = "existingCount")]
    pub existing_count: u32,
    #[serde(rename = "missingCount")]
    pub missing_count: u32,
    pub groups: Vec<GroupHealthItem>,
}

struct PreparedImport {
    groups: Groups,
    group_count: u32,
    file_count: u32,
    skipped_groups: u32,
}

fn normalize_components(path: PathBuf) -> PathBuf {
    let mut out = PathBuf::new();
    for component in path.components() {
        match component {
            Component::CurDir => {}
            Component::ParentDir => {
                let _ = out.pop();
            }
            _ => out.push(component.as_os_str()),
        }
    }
    out
}

fn normalize_file_path(file_path: &str) -> Result<Option<String>, String> {
    let trimmed = file_path.trim();
    if trimmed.is_empty() {
        return Ok(None);
    }

    let path = PathBuf::from(trimmed);
    let absolute = if path.is_absolute() {
        path
    } else {
        let cwd = std::env::current_dir().map_err(|e| format!("读取当前目录失败: {e}"))?;
        cwd.join(path)
    };

    let normalized = normalize_components(absolute);
    let value = normalized
        .to_string_lossy()
        .replace('/', "\\")
        .trim()
        .to_string();

    if value.is_empty() {
        return Ok(None);
    }
    Ok(Some(value))
}

fn identity_key(file_path: &str) -> Result<Option<String>, String> {
    let normalized = normalize_file_path(file_path)?;
    Ok(normalized.map(|p| p.to_lowercase()))
}

fn groups_file_path(app: &AppHandle) -> Result<PathBuf, String> {
    let app_data_dir = app
        .path()
        .app_data_dir()
        .map_err(|e| format!("获取应用数据目录失败: {e}"))?;
    fs::create_dir_all(&app_data_dir).map_err(|e| format!("创建应用数据目录失败: {e}"))?;
    Ok(app_data_dir.join(GROUPS_FILE_NAME))
}

fn groups_data_dir(app: &AppHandle) -> Result<PathBuf, String> {
    let app_data_dir = app
        .path()
        .app_data_dir()
        .map_err(|e| format!("获取应用数据目录失败: {e}"))?;
    fs::create_dir_all(&app_data_dir).map_err(|e| format!("创建应用数据目录失败: {e}"))?;
    Ok(app_data_dir)
}

pub fn normalize_and_dedupe(files: &[String]) -> Result<Vec<String>, String> {
    let mut seen = HashSet::new();
    let mut out = Vec::new();

    for file in files {
        let normalized = normalize_file_path(file)?;
        let Some(normalized) = normalized else {
            continue;
        };
        let key = normalized.to_lowercase();
        if seen.insert(key) {
            out.push(normalized);
        }
    }

    Ok(out)
}

fn validate_group_name(name: &str) -> Result<&str, String> {
    let group_name = name.trim();
    if group_name.is_empty() {
        return Err("文件组名称不能为空".to_string());
    }
    Ok(group_name)
}

fn validate_rename_request(
    old_name: &str,
    new_name: &str,
    old_exists: bool,
    new_exists: bool,
) -> Result<(), String> {
    validate_group_name(old_name)?;
    validate_group_name(new_name)?;

    if !old_exists {
        return Err("原文件组不存在".to_string());
    }
    if old_name != new_name && new_exists {
        return Err("目标文件组名称已存在".to_string());
    }

    Ok(())
}

fn make_import_group_name(name: &str, existing: &HashSet<String>) -> String {
    let base = name.trim();
    if !existing.contains(base) {
        return base.to_string();
    }

    let first = format!("{base} (导入)");
    if !existing.contains(&first) {
        return first;
    }

    let mut index = 2;
    loop {
        let candidate = format!("{base} (导入 {index})");
        if !existing.contains(&candidate) {
            return candidate;
        }
        index += 1;
    }
}

fn prepare_import_groups(raw: Groups, existing_names: &HashSet<String>) -> Result<PreparedImport, String> {
    let mut names = existing_names.clone();
    let mut groups = Groups::new();
    let mut file_count = 0_u32;
    let mut skipped_groups = 0_u32;

    for (name, files) in raw {
        let trimmed = name.trim();
        if trimmed.is_empty() {
            skipped_groups += 1;
            continue;
        }

        let normalized_files = normalize_and_dedupe(&files)?;
        if normalized_files.is_empty() {
            skipped_groups += 1;
            continue;
        }

        let next_name = make_import_group_name(trimmed, &names);
        names.insert(next_name.clone());
        file_count += normalized_files.len() as u32;
        groups.insert(next_name, normalized_files);
    }

    Ok(PreparedImport {
        group_count: groups.len() as u32,
        groups,
        file_count,
        skipped_groups,
    })
}

pub fn build_health_report(groups: &Groups) -> Result<GroupHealthReport, String> {
    let mut report_groups = Vec::new();
    let mut file_count = 0_u32;
    let mut existing_count = 0_u32;
    let mut missing_count = 0_u32;

    for (name, files) in groups {
        let mut existing = 0_u32;
        let mut missing_files = Vec::new();

        for file in files {
            let Some(normalized) = normalize_file_path(file)? else {
                continue;
            };

            file_count += 1;
            if PathBuf::from(&normalized).exists() {
                existing += 1;
                existing_count += 1;
            } else {
                missing_count += 1;
                missing_files.push(normalized);
            }
        }

        report_groups.push(GroupHealthItem {
            name: name.clone(),
            existing,
            total: files.len() as u32,
            missing_files,
        });
    }

    Ok(GroupHealthReport {
        group_count: groups.len() as u32,
        file_count,
        existing_count,
        missing_count,
        groups: report_groups,
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn normalize_and_dedupe_trims_absolute_paths_and_removes_duplicates() {
        let cwd = std::env::current_dir().expect("cwd");
        let expected = normalize_components(cwd.join("Cargo.toml"))
            .to_string_lossy()
            .replace('/', "\\");

        let files = vec![
            " ./Cargo.toml ".to_string(),
            ".\\Cargo.toml".to_string(),
            "".to_string(),
        ];

        let result = normalize_and_dedupe(&files).expect("dedupe");

        assert_eq!(result, vec![expected]);
    }

    #[test]
    fn validate_group_name_rejects_blank_names() {
        let error = validate_group_name("   ").expect_err("blank name should fail");

        assert_eq!(error, "文件组名称不能为空");
    }

    #[test]
    fn validate_rename_request_rejects_missing_original_group() {
        let error = validate_rename_request("old", "new", false, false)
            .expect_err("missing original should fail");

        assert_eq!(error, "原文件组不存在");
    }

    #[test]
    fn validate_rename_request_rejects_existing_target_group() {
        let error = validate_rename_request("old", "new", true, true)
            .expect_err("existing target should fail");

        assert_eq!(error, "目标文件组名称已存在");
    }

    #[test]
    fn make_import_group_name_avoids_existing_names() {
        let existing = HashSet::from([
            "docs".to_string(),
            "docs (导入)".to_string(),
            "docs (导入 2)".to_string(),
        ]);

        let name = make_import_group_name(" docs ", &existing);

        assert_eq!(name, "docs (导入 3)");
    }

    #[test]
    fn prepare_import_groups_sanitizes_names_files_and_conflicts() {
        let existing = HashSet::from(["docs".to_string()]);
        let mut raw = Groups::new();
        raw.insert(
            " docs ".to_string(),
            vec![
                " ./Cargo.toml ".to_string(),
                ".\\Cargo.toml".to_string(),
                "".to_string(),
            ],
        );
        raw.insert("   ".to_string(), vec!["./Cargo.toml".to_string()]);

        let prepared = prepare_import_groups(raw, &existing).expect("prepare import");

        assert_eq!(prepared.group_count, 1);
        assert_eq!(prepared.file_count, 1);
        assert!(prepared.groups.contains_key("docs (导入)"));
    }

    #[test]
    fn build_health_report_separates_existing_and_missing_files() {
        let existing = std::env::current_dir()
            .expect("cwd")
            .join("Cargo.toml")
            .to_string_lossy()
            .to_string();
        let mut groups = Groups::new();
        groups.insert(
            "workspace".to_string(),
            vec![existing.clone(), ".\\definitely-missing-health-test.file".to_string()],
        );

        let report = build_health_report(&groups).expect("health report");

        assert_eq!(report.group_count, 1);
        assert_eq!(report.file_count, 2);
        assert_eq!(report.existing_count, 1);
        assert_eq!(report.missing_count, 1);
        assert_eq!(report.groups[0].name, "workspace");
        assert_eq!(report.groups[0].existing, 1);
        assert_eq!(report.groups[0].total, 2);
        assert_eq!(report.groups[0].missing_files.len(), 1);
        assert!(report.groups[0].missing_files[0].ends_with("definitely-missing-health-test.file"));
    }
}

pub fn load_groups(app: &AppHandle) -> Result<Groups, String> {
    let path = groups_file_path(app)?;
    if !path.exists() {
        return Ok(BTreeMap::new());
    }

    let content = fs::read_to_string(&path).map_err(|e| format!("读取分组文件失败: {e}"))?;
    if content.trim().is_empty() {
        return Ok(BTreeMap::new());
    }

    serde_json::from_str::<Groups>(&content).map_err(|e| format!("解析分组文件失败: {e}"))
}

pub fn write_groups(app: &AppHandle, groups: &Groups) -> Result<(), String> {
    let path = groups_file_path(app)?;
    let json = serde_json::to_string_pretty(groups).map_err(|e| format!("序列化分组失败: {e}"))?;
    fs::write(path, json).map_err(|e| format!("写入分组文件失败: {e}"))
}

pub fn groups_file_path_display(app: &AppHandle) -> Result<String, String> {
    Ok(groups_file_path(app)?.to_string_lossy().to_string())
}

pub fn export_groups_to_path(app: &AppHandle, target_path: &str) -> Result<ExportGroupsResult, String> {
    let target_path = target_path.trim();
    if target_path.is_empty() {
        return Err("导出路径不能为空".to_string());
    }

    let groups = load_groups(app)?;
    let file_count = groups.values().map(|files| files.len() as u32).sum();
    let json = serde_json::to_string_pretty(&groups).map_err(|e| format!("序列化分组失败: {e}"))?;
    fs::write(target_path, json).map_err(|e| format!("导出分组失败: {e}"))?;

    Ok(ExportGroupsResult {
        group_count: groups.len() as u32,
        file_count,
        path: target_path.to_string(),
    })
}

pub fn import_groups_from_path(app: &AppHandle, source_path: &str) -> Result<ImportGroupsResult, String> {
    let source_path = source_path.trim();
    if source_path.is_empty() {
        return Err("导入路径不能为空".to_string());
    }

    let content = fs::read_to_string(source_path).map_err(|e| format!("读取导入文件失败: {e}"))?;
    let raw = serde_json::from_str::<Groups>(&content).map_err(|e| format!("解析导入文件失败: {e}"))?;
    let mut groups = load_groups(app)?;
    let existing = groups.keys().cloned().collect::<HashSet<_>>();
    let prepared = prepare_import_groups(raw, &existing)?;

    for (name, files) in prepared.groups {
        groups.insert(name, files);
    }

    write_groups(app, &groups)?;
    Ok(ImportGroupsResult {
        group_count: prepared.group_count,
        file_count: prepared.file_count,
        skipped_groups: prepared.skipped_groups,
        path: source_path.to_string(),
    })
}

pub fn open_data_dir(app: &AppHandle) -> Result<String, String> {
    let dir = groups_data_dir(app)?;
    open_path(&dir)?;
    Ok(dir.to_string_lossy().to_string())
}

fn open_path(path: &Path) -> Result<(), String> {
    #[cfg(target_os = "windows")]
    {
        Command::new("explorer")
            .arg(path)
            .status()
            .map_err(|e| format!("打开数据目录失败: {e}"))?;
        return Ok(());
    }

    #[cfg(target_os = "macos")]
    {
        Command::new("open")
            .arg(path)
            .status()
            .map_err(|e| format!("打开数据目录失败: {e}"))?;
        return Ok(());
    }

    #[cfg(all(unix, not(target_os = "macos")))]
    {
        Command::new("xdg-open")
            .arg(path)
            .status()
            .map_err(|e| format!("打开数据目录失败: {e}"))?;
        return Ok(());
    }

    #[allow(unreachable_code)]
    Err("当前平台不支持打开数据目录".to_string())
}

pub fn save_group(app: &AppHandle, name: &str, files: &[String]) -> Result<(), String> {
    let group_name = validate_group_name(name)?;

    let normalized_files = normalize_and_dedupe(files)?;
    if normalized_files.is_empty() {
        return Err("文件列表不能为空".to_string());
    }

    let mut groups = load_groups(app)?;
    groups.insert(group_name.to_string(), normalized_files);
    write_groups(app, &groups)
}

pub fn rename_group(app: &AppHandle, old_name: &str, new_name: &str) -> Result<(), String> {
    let old_name = old_name.trim();
    let new_name = new_name.trim();

    let mut groups = load_groups(app)?;
    validate_rename_request(
        old_name,
        new_name,
        groups.contains_key(old_name),
        groups.contains_key(new_name),
    )?;

    let files = groups
        .remove(old_name)
        .ok_or_else(|| "原文件组不存在".to_string())?;
    groups.insert(new_name.to_string(), files);
    write_groups(app, &groups)
}

pub fn delete_group(app: &AppHandle, name: &str) -> Result<(), String> {
    let name = validate_group_name(name)?;

    let mut groups = load_groups(app)?;
    groups.remove(name);
    write_groups(app, &groups)
}

pub fn update_group_files(app: &AppHandle, name: &str, files: &[String]) -> Result<(), String> {
    let name = validate_group_name(name)?;

    let mut groups = load_groups(app)?;
    if !groups.contains_key(name) {
        return Err("文件组不存在".to_string());
    }

    let normalized_files = normalize_and_dedupe(files)?;
    groups.insert(name.to_string(), normalized_files);
    write_groups(app, &groups)
}

pub fn group_stats(app: &AppHandle, name: &str) -> Result<(u32, u32), String> {
    let name = name.trim();
    if name.is_empty() {
        return Ok((0, 0));
    }

    let groups = load_groups(app)?;
    let Some(files) = groups.get(name) else {
        return Ok((0, 0));
    };

    let mut total = 0_u32;
    let mut existing = 0_u32;
    for file in files {
        total += 1;
        if let Ok(Some(path)) = normalize_file_path(file) {
            if PathBuf::from(path).exists() {
                existing += 1;
            }
        }
    }

    Ok((existing, total))
}

pub fn groups_health(app: &AppHandle) -> Result<GroupHealthReport, String> {
    let groups = load_groups(app)?;
    build_health_report(&groups)
}

pub fn dedupe_for_open(files: &[String]) -> Result<Vec<String>, String> {
    let mut seen = HashSet::new();
    let mut out = Vec::new();

    for file in files {
        let normalized = normalize_file_path(file)?;
        let Some(normalized) = normalized else {
            continue;
        };
        let key = identity_key(&normalized)?.unwrap_or_default();
        if !key.is_empty() && seen.insert(key) {
            out.push(normalized);
        }
    }

    Ok(out)
}
