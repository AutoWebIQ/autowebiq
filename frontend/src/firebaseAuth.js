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

const firebaseConfig = {
  apiKey: "AIzaSyD2OSwdJVrjzf5vMQDfBBTPMaOK0u7xrLE",
  authDomain: "autowebiq.firebaseapp.com",
  projectId: "autowebiq",
  storageBucket: "autowebiq.appspot.com",
  messagingSenderId: "969088932092",
  appId: "1:969088932092:web:0c3ea8d0fce30d"
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
