use std::collections::BTreeMap;
use std::fs;
use std::path::PathBuf;

use tauri::{AppHandle, Manager};

use crate::services::group_service::{normalize_and_dedupe, write_groups, Groups};

const LEGACY_FILE_NAME: &str = "file_groups.json";
const MIGRATION_MARKER: &str = ".migration_v1_done";

#[derive(serde::Serialize)]
pub struct MigrationResult {
    pub migrated: bool,
    pub source: Option<String>,
}

fn marker_path(app: &AppHandle) -> Result<PathBuf, String> {
    let app_data_dir = app
        .path()
        .app_data_dir()
        .map_err(|e| format!("获取应用数据目录失败: {e}"))?;
    fs::create_dir_all(&app_data_dir).map_err(|e| format!("创建应用数据目录失败: {e}"))?;
    Ok(app_data_dir.join(MIGRATION_MARKER))
}

fn legacy_candidates() -> Vec<PathBuf> {
    let mut out = Vec::new();

    if let Ok(cwd) = std::env::current_dir() {
        out.push(cwd.join(LEGACY_FILE_NAME));
        out.push(cwd.join("src").join(LEGACY_FILE_NAME));
    }

    if let Ok(exe) = std::env::current_exe() {
        if let Some(parent) = exe.parent() {
            out.push(parent.join(LEGACY_FILE_NAME));
            out.push(parent.join("src").join(LEGACY_FILE_NAME));
        }
    }

    out
}

fn read_legacy_groups(path: &PathBuf) -> Result<Groups, String> {
    let content = fs::read_to_string(path).map_err(|e| format!("读取旧数据失败: {e}"))?;
    let raw =
        serde_json::from_str::<BTreeMap<String, Vec<String>>>(&content).map_err(|e| format!("解析旧数据失败: {e}"))?;

    let mut normalized = BTreeMap::new();
    for (name, files) in raw {
        let deduped = normalize_and_dedupe(&files)?;
        normalized.insert(name.trim().to_string(), deduped);
    }
    Ok(normalized)
}

pub fn migrate_legacy_groups(app: &AppHandle) -> Result<MigrationResult, String> {
    let marker = marker_path(app)?;
    if marker.exists() {
        return Ok(MigrationResult {
            migrated: false,
            source: None,
        });
    }

    for candidate in legacy_candidates() {
        if !candidate.exists() {
            continue;
        }

        let groups = read_legacy_groups(&candidate)?;
        if groups.is_empty() {
            continue;
        }

        write_groups(app, &groups)?;
        fs::write(&marker, b"migrated").map_err(|e| format!("写入迁移标记失败: {e}"))?;

        return Ok(MigrationResult {
            migrated: true,
            source: Some(candidate.to_string_lossy().to_string()),
        });
    }

    fs::write(&marker, b"no-legacy-found").map_err(|e| format!("写入迁移标记失败: {e}"))?;
    Ok(MigrationResult {
        migrated: false,
        source: None,
    })
}
