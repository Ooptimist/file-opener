use std::path::Path;
use std::process::Command;

#[derive(serde::Serialize)]
pub struct OpenFilesResult {
    #[serde(rename = "successCount")]
    pub success_count: u32,
    #[serde(rename = "failedFiles")]
    pub failed_files: Vec<String>,
}

fn is_uac_related_failure(stderr: &str) -> bool {
    let text = stderr.to_lowercase();
    text.contains("requires elevation")
        || text.contains("access is denied")
        || text.contains("operation was canceled by the user")
}

fn open_single_file(path: &str) -> bool {
    if !Path::new(path).exists() {
        return false;
    }

    #[cfg(target_os = "windows")]
    {
        let status = Command::new("cmd")
            .args(["/C", "start", "", path])
            .status();
        return status.map(|s| s.success()).unwrap_or(false);
    }

    #[cfg(target_os = "macos")]
    {
        let status = Command::new("open").arg(path).status();
        return status.map(|s| s.success()).unwrap_or(false);
    }

    #[cfg(all(unix, not(target_os = "macos")))]
    {
        let status = Command::new("xdg-open").arg(path).status();
        return status.map(|s| s.success()).unwrap_or(false);
    }

    #[allow(unreachable_code)]
    false
}

pub fn open_files(files: &[String]) -> OpenFilesResult {
    let mut result = OpenFilesResult {
        success_count: 0,
        failed_files: Vec::new(),
    };

    for file in files {
        if !Path::new(file).exists() {
            result.failed_files.push(file.clone());
            continue;
        }

        let ok = open_single_file(file);
        if ok {
            result.success_count += 1;
        } else {
            result.failed_files.push(file.clone());
        }
    }

    result
}

#[allow(dead_code)]
fn _unused_keep_behavior_for_future(stderr: &str) -> bool {
    is_uac_related_failure(stderr)
}
