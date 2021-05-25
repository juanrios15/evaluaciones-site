            
            
function loginsocial(tipo) {
  
  var firebaseConfig = {
    apiKey: "AIzaSyDdKQSEwCGvp-GTxctJPNH3UU475646Ots",
    authDomain: "evaluaciones-app.firebaseapp.com",
    projectId: "evaluaciones-app",
    storageBucket: "evaluaciones-app.appspot.com",
    messagingSenderId: "854882954870",
    appId: "1:854882954870:web:472e6d760322bf0a36b957",
    measurementId: "G-20K7JL0S75"
  };
  // Initialize Firebase
  firebase.initializeApp(firebaseConfig);
  firebase.analytics();
  
  if (tipo == 1) {
    var provider = new firebase.auth.GoogleAuthProvider();
  }
  else if (tipo == 2) {
    var provider = new firebase.auth.FacebookAuthProvider();
  }

  firebase
  .auth()
  .signInWithPopup(provider)
  .then((result) => {
    /** @type {firebase.auth.OAuthCredential} */
    var credential = result.credential;
    // The signed-in user info.
    var user = result.user;
    // This gives you a Facebook Access Token. You can use it to access the Facebook API.
    var accessToken = credential.accessToken;

    console.log(user);

    user.getIdToken().then(
      function(idToken) {
          var data = {'token_id':idToken}
          axios.post('/api/sociallogin/',data).then(
            function(response){

              if(document.referrer.split('/')[2]!=location.hostname){
                //User came from other domain or from direct
                window.location.href = '/';
              }else{
                //User came from another page on your site
                window.history.go(-1)
              }
            }
        )
          
      }).catch(function(error){
        console.log(error);
      })

    // ...
  })
  .catch((error) => {
    // Handle Errors here.
    // var errorCode = error.code;
    // var errorMessage = error.message;
    // // The email of the user's account used.
    // var email = error.email;
    // // The firebase.auth.AuthCredential type that was used.
    // var credential = error.credential;

    console.log(error);

    // ...
  });
}


