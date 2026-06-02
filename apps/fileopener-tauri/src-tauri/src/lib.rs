mod services;

use serde::Serialize;
use tauri::AppHandle;

use services::file_open_service::{open_files as open_files_service, OpenFilesResult};
use services::group_service as group;
use services::migration_service::{migrate_legacy_groups as migrate_legacy_groups_service, MigrationResult};

#[derive(Serialize)]
struct GroupStats {
    existing: u32,
    total: u32,
}

#[tauri::command]
fn load_groups(app: AppHandle) -> Result<group::Groups, String> {
    group::load_groups(&app)
}

#[tauri::command]
fn save_group(app: AppHandle, name: String, files: Vec<String>) -> Result<(), String> {
    group::save_group(&app, &name, &files)
}

#[tauri::command]
fn rename_group(app: AppHandle, old_name: String, new_name: String) -> Result<(), String> {
    group::rename_group(&app, &old_name, &new_name)
}

#[tauri::command]
fn delete_group(app: AppHandle, name: String) -> Result<(), String> {
    group::delete_group(&app, &name)
}

#[tauri::command]
fn update_group_files(app: AppHandle, name: String, files: Vec<String>) -> Result<(), String> {
    group::update_group_files(&app, &name, &files)
}

#[tauri::command]
fn get_group_stats(app: AppHandle, name: String) -> Result<GroupStats, String> {
    let (existing, total) = group::group_stats(&app, &name)?;
    Ok(GroupStats { existing, total })
}

#[tauri::command]
fn open_files(_app: AppHandle, files: Vec<String>) -> Result<OpenFilesResult, String> {
    let deduped = group::dedupe_for_open(&files)?;
    Ok(open_files_service(&deduped))
}

#[tauri::command]
fn migrate_legacy_groups(app: AppHandle) -> Result<MigrationResult, String> {
    migrate_legacy_groups_service(&app)
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_dialog::init())
        .setup(|app| {
            if cfg!(debug_assertions) {
                app.handle().plugin(
                    tauri_plugin_log::Builder::default()
                        .level(log::LevelFilter::Info)
                        .build(),
                )?;
            }
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            load_groups,
            save_group,
            rename_group,
            delete_group,
            update_group_files,
            get_group_stats,
            open_files,
            migrate_legacy_groups
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
