const { contextBridge } = require('electron');
contextBridge.exposeInMainWorld('bmsDesktop', {
  isDesktop: true,
  version: '16.0.0'
});
