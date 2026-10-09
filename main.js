const { app, BrowserWindow, dialog } = require('electron');
const { spawn } = require('child_process');
const path = require('path');
const http = require('http');

let backend = null;
const PORT = 8765;

function pythonCommand() {
  return process.platform === 'win32' ? 'python' : 'python3';
}

function startBackend() {
  const backendDir = path.join(__dirname, 'app', 'backend');
  backend = spawn(pythonCommand(), ['-m', 'uvicorn', 'app:app', '--host', '127.0.0.1', '--port', String(PORT)], {
    cwd: backendDir,
    windowsHide: true,
    stdio: 'ignore'
  });
  backend.on('error', () => {});
}

function waitForBackend(retries = 40) {
  return new Promise(resolve => {
    const check = () => {
      const req = http.get(`http://127.0.0.1:${PORT}/api/health`, res => {
        res.resume();
        if (res.statusCode >= 200 && res.statusCode < 500) return resolve(true);
        retry();
      });
      req.on('error', retry);
      req.setTimeout(500, () => { req.destroy(); retry(); });
    };
    const retry = () => retries-- > 0 ? setTimeout(check, 250) : resolve(false);
    check();
  });
}

async function createWindow() {
  const win = new BrowserWindow({
    width: 1440,
    height: 950,
    minWidth: 1100,
    minHeight: 720,
    backgroundColor: '#f4f7fb',
    title: 'BMS – Bone & Implant Measurement System',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false
    }
  });
  win.removeMenu();
  const ok = await waitForBackend();
  if (!ok) {
    await dialog.showMessageBox(win, {
      type: 'warning',
      title: 'BMS backend unavailable',
      message: 'BMS could not start its local measurement service. Install Python and the packages in app/requirements.txt, then restart BMS.'
    });
  }
  await win.loadFile(path.join(__dirname, 'app', 'frontend', 'index.html'));
}

app.whenReady().then(() => {
  startBackend();
  createWindow();
  app.on('activate', () => { if (BrowserWindow.getAllWindows().length === 0) createWindow(); });
});

app.on('window-all-closed', () => {
  if (backend) backend.kill();
  if (process.platform !== 'darwin') app.quit();
});
app.on('before-quit', () => { if (backend) backend.kill(); });
