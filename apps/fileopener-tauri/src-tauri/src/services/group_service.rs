use std::collections::{BTreeMap, HashSet};
use std::fs;
use std::path::{Component, PathBuf};

use tauri::{AppHandle, Manager};

pub type Groups = BTreeMap<String, Vec<String>>;

const GROUPS_FILE_NAME: &str = "file_groups.json";

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

pub fn save_group(app: &AppHandle, name: &str, files: &[String]) -> Result<(), String> {
    let group_name = name.trim();
    if group_name.is_empty() {
        return Err("文件组名称不能为空".to_string());
    }

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

    if old_name.is_empty() || new_name.is_empty() {
        return Err("文件组名称不能为空".to_string());
    }

    let mut groups = load_groups(app)?;
    if !groups.contains_key(old_name) {
        return Err("原文件组不存在".to_string());
    }
    if old_name != new_name && groups.contains_key(new_name) {
        return Err("目标文件组名称已存在".to_string());
    }

    let files = groups
        .remove(old_name)
        .ok_or_else(|| "原文件组不存在".to_string())?;
    groups.insert(new_name.to_string(), files);
    write_groups(app, &groups)
}

pub fn delete_group(app: &AppHandle, name: &str) -> Result<(), String> {
    let name = name.trim();
    if name.is_empty() {
        return Err("文件组名称不能为空".to_string());
    }

    let mut groups = load_groups(app)?;
    groups.remove(name);
    write_groups(app, &groups)
}

pub fn update_group_files(app: &AppHandle, name: &str, files: &[String]) -> Result<(), String> {
    let name = name.trim();
    if name.is_empty() {
        return Err("文件组名称不能为空".to_string());
    }

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
