$(document).ready(function(){
    $('.dropdown-trigger').dropdown({coverTrigger: false, constrainWidth: false});
    $('.sidenav').sidenav();
    $(".dropdown-content>li>a").css("color", "white");
    $(".sidenav>li>a").css("color", "white");
});