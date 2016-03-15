//code from http://www.w3schools.com/html/html5_geolocation.asp
var x = document.getElementById("successfully_grabbed_location");

function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(showPosition);
    } else {
        x.innerHTML = "Geolocation is not supported by this browser.";
    }
}

function showPosition(position) {
    document.getElementById("current_location_latitude").value = position.coords.latitude;
    document.getElementById("current_location_longitude").value = position.coords.longitude;
    //console.log("got latitude/longitudde", position);
    x.innerHTML =
        //"<div data-role='popup'>" +
        //    "<a href='#' data-rel='back' class='ui-btn ui-icon-delete ui-btn-right ui-btn-icon-notext'>Close</a>" +
            "Fooddy is now using your current location to recommend restaurants!";
        //"</div>";
    //x.innerHTML("Hey wsup bruh");
}

//function getNextEventLocation(target) {
//    document.getElementById(target).style.display='block';
//}
//
//
//function openAddressForm(target) {
//    document.getElementById(target).style.display='block';
//}
