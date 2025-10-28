// Firebase Auth utility functions for React components
// Uses Firebase SDK initialized in index.html

export const getFirebaseAuth = () => {
  if (!window.firebaseAuth) {
    throw new Error('Firebase not initialized. Make sure index.html loads Firebase SDK first.');
  }
  return window.firebaseAuth;
};

export const getFirebaseApp = () => {
  if (!window.firebaseApp) {
    throw new Error('Firebase not initialized. Make sure index.html loads Firebase SDK first.');
  }
  return window.firebaseApp;
};

// Import Firebase Auth methods dynamically
export const loadFirebaseAuthMethods = async () => {
  const {
    createUserWithEmailAndPassword,
    signInWithEmailAndPassword,
    signInWithPopup,
    GoogleAuthProvider,
    GithubAuthProvider,
    sendPasswordResetEmail,
    signOut,
    onAuthStateChanged
  } = await import('https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js');
  
  return {
    createUserWithEmailAndPassword,
    signInWithEmailAndPassword,
    signInWithPopup,
    GoogleAuthProvider,
    GithubAuthProvider,
    sendPasswordResetEmail,
    signOut,
    onAuthStateChanged
  };
};
