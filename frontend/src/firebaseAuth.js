// Firebase Auth Helper - Proper SDK imports for production build
import { initializeApp } from 'firebase/app';
import {
  getAuth,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signInWithPopup,
  GoogleAuthProvider,
  GithubAuthProvider,
  signOut,
  onAuthStateChanged
} from 'firebase/auth';

// Firebase configuration from environment variables (with fallbacks)
const firebaseConfig = {
  apiKey: process.env.REACT_APP_FIREBASE_API_KEY || "AIzaSyD2OSwdJVrjzf5vMQDfBBTPMaOK0u7xrLE",
  authDomain: process.env.REACT_APP_FIREBASE_AUTH_DOMAIN || "autowebiq.firebaseapp.com",
  projectId: process.env.REACT_APP_FIREBASE_PROJECT_ID || "autowebiq",
  storageBucket: process.env.REACT_APP_FIREBASE_STORAGE_BUCKET || "autowebiq.appspot.com",
  messagingSenderId: process.env.REACT_APP_FIREBASE_MESSAGING_SENDER_ID || "969088932092",
  appId: process.env.REACT_APP_FIREBASE_APP_ID || "1:969088932092:web:0c3ea8d0fce30d"
};

let app;
let auth;

export function getFirebaseAuth() {
  if (!app) {
    app = initializeApp(firebaseConfig);
    auth = getAuth(app);
  }
  return auth;
}

export function loadFirebaseAuthMethods() {
  return {
    signInWithEmailAndPassword,
    createUserWithEmailAndPassword,
    signInWithPopup,
    GoogleAuthProvider,
    GithubAuthProvider,
    signOut,
    onAuthStateChanged
  };
}
