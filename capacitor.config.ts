
import { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.urokiislama.app',
  appName: 'Уроки Ислама',
  webDir: 'frontend/build',
  bundledWebRuntime: false,
  server: {
    androidScheme: 'https'
  },
  plugins: {
    SplashScreen: {
      launchShowDuration: 2000,
      backgroundColor: '#14b8a6',
      showSpinner: false
    },
    StatusBar: {
      style: 'DARK',
      backgroundColor: '#14b8a6'
    },
    Keyboard: {
      resize: 'body',
      style: 'dark',
      resizeOnFullScreen: true
    }
  }
};

export default config;
