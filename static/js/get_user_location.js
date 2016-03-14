//code from http://www.w3schools.com/html/html5_geolocation.asp
var x = document.getElementById("current_location");

function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(showPosition);
    } else {
        x.innerHTML = "Geolocation is not supported by this browser.";
    }
}

function showPosition(position) {
    x.innerHTML = "Latitude: " + position.coords.latitude +
    "<br>Longitude: " + position.coords.longitude;
}

//function getNextEventLocation(target) {
//    document.getElementById(target).style.display='block';
//}
//
//
//function openAddressForm(target) {
//    document.getElementById(target).style.display='block';
//}
