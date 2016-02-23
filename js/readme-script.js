(function() {
  'use strict';

  var URLs = {},
  REPO;

  REPO = getRepo();
  URLs.readme = 'https://api.github.com/repos/' + REPO + '/contents/README.md';
  URLs.markdown = 'https://api.github.com/markdown';

  getResource( URLs.readme, onReadme );

  // FUNCTIONS //

  function getRepo() {
    return document.getElementById( 'readme' ).getAttribute( 'repo' );
  }

  function onReadme( blob ) {
    var content = window.atob( JSON.parse( blob ).content );
    render( content );
  }

  function onResource( html ) {
    var search = new RegExp('src="images/', 'g');
    html = html.replace(search, 'src="https://raw.githubusercontent.com/' + REPO + '/master/images/');
    document.getElementById( 'readme' ).innerHTML = html;
    document.title = $('h1').text();
  }

  function getResource( url, clbk ) {
    var xhr;
    if ( url && clbk ) {
      xhr = new XMLHttpRequest();
      xhr.open( 'GET', url );

      xhr.onreadystatechange = function () {
        if ( xhr.readyState != 4 || xhr.status != 200 ){
          return;
        }
        clbk( xhr.responseText );
      };
      xhr.send();
    }
  }

  function postResource( url, data, clbk ) {
    var xhr;
    if ( url && clbk ) {
      xhr = new XMLHttpRequest();
      xhr.open( 'POST', url, true );

      xhr.setRequestHeader( 'Content-Type', 'application/json' );

      xhr.onreadystatechange = function () {
        if ( xhr.readyState != 4 || xhr.status != 200 ){
          return;
        }
        clbk( xhr.responseText );
      };
      xhr.send( data );
    }
  }

  function render( content ) {
    content = {
      'text': content,
      'mode': 'markdown',
      'context': REPO
    };
    content = JSON.stringify( content );
    postResource( URLs.markdown, content, onResource );
  }
})();
