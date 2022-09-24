jQuery(function ($) {
  $(".sidebar-dropdown > a").click(function() {
    $(".sidebar-submenu").slideUp(200);
    if ( $(this).parent().hasClass("active")) {
      $(".sidebar-dropdown").removeClass("active");
      $(this).parent().removeClass("active");
    } else {
      $(".sidebar-dropdown").removeClass("active");
      $(this).next(".sidebar-submenu").slideDown(200);
      $(this).parent().addClass("active");
    }
});

  $("#close-sidebar").click(function(e) {
    //e.preventDefault();
    $(".page-wrapper").removeClass("toggled");
    $(".logo").addClass("active");

  });

  $("#show-sidebar").click(function(e) {
    //e.preventDefault();
    $(".page-wrapper").addClass("toggled");
    $(".logo").removeClass("active");

  });
});

function passwordShowHidde(id){
  var tipo = $('#'+id).attr('type');
  if(tipo == 'password') {
      //$(this).next('input').attr('type','text');
      $('#'+id).attr('type','text');
      //console.log('#'+id+'-eye');
      $('#'+id+'-eye').removeClass('ti-eye');
      $('#'+id+'-eye').addClass('ti-eye-off');
  } else {
      //$(this).next('input').attr('type','password');
      $('#'+id).attr('type','password');
      $('#'+id+'-eye').addClass('ti-eye');
      $('#'+id+'-eye').removeClass('ti-eye-off');
  }
}
