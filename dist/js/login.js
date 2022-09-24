var getBrowserInfo = function() {
  var ua= navigator.userAgent, tem, 
  M= ua.match(/(opera|chrome|safari|firefox|msie|trident(?=\/))\/?\s*(\d+)/i) || [];
  if(/trident/i.test(M[1])){
      tem=  /\brv[ :]+(\d+)/g.exec(ua) || [];
      return 'IE '+(tem[1] || '');
  }
  if(M[1]=== 'Chrome'){
      tem= ua.match(/\b(OPR|Edge)\/(\d+)/);
      if(tem!= null) return tem.slice(1).join(' ').replace('OPR', 'Opera');
  }
  M= M[2]? [M[1], M[2]]: [navigator.appName, navigator.appVersion, '-?'];
  if((tem= ua.match(/version\/(\d+)/i))!= null) M.splice(1, 1, tem[1]);
  return M.join(' ');
};

function getMsg(){
  return "En su navegador web, active por favor las ventanas emergentes para este sitio, posteriormente actualice esta página o presione la tecla F5";
}
function showMessagePopupbloqueados(){
  var tipoNavegador = getBrowserInfo();
  var retMsgPopup = false;
  //console.log(tipoNavegador.includes("Chrome"))
  var sms = getMsg();
  var img = '';
  if(tipoNavegador.includes("Chrome")){
    img = '/static/Popups bloqueados.png';
  }else if(tipoNavegador.includes("Firefox")){
    img = '/static/firefox.png'
  }
  if (img.length == 0){
    //alert("su navegador no es compatible");
    Swal.fire({
      icon: 'error',
      title: 'Ups... Este navegador no es compatible con el sistema',
      html:
        'Utiliza por favor otra opción como: ' +
        '<a href="https://www.mozilla.org/es-MX/firefox/"><b>Firefox</b></a>, o bien ' +
        '<a href="https://www.google.com/chrome/"><b>chrome</b></a> ',
      showCancelButton: false,
      allowEscapeKey: false,
      allowEnterKey : false,
      allowOutsideClick : false,
      didOpen: (resp) => {
        Swal.showLoading();
      }
    });
  }else{
    retMsgPopup = true;
    Swal.fire({
      icon: 'error',
      title: 'Los Popups están bloqueados para este sitio!!!',
      text: sms,
      imageUrl: img,
      imageWidth: 400,
      imageHeight: 200,
      imageAlt: 'Popups bloqueados',
      showCancelButton: false,
      allowEscapeKey: false,
      allowEnterKey : false,
      allowOutsideClick : false,
      didOpen: (resp) => {
        Swal.showLoading();
      }
    });
  }
  return retMsgPopup;
}

function testPopupsAlertaNavegacion(){
  // realizar un test para ver si se pueden abrir popups
  var win = window.open("/popups", '_blank');
  //console.log (getBrowserInfo());
  var testPopups = false;
  if(win){
    //win.focus(); //Browser has allowed it to be opened
    win.close();
    testPopups = true;
  }else{
    resp = showMessagePopupbloqueados();
    if (resp){
      $("#btnAcceder").addClass("disabled");
      $("#smsInvali").html("<p class='text-red'>"+ getMsg() +"</p>");
    }
  }
  return testPopups;
}

