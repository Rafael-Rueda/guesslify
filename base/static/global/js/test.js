// document.addEventListener('DOMContentLoaded', function () {
//     window.addEventListener('beforeunload', function (e) {
//         // Make an asynchronous request to log the user out
//         var xhr = new XMLHttpRequest();
//         xhr.open('POST', '/delete_user/', true);
//         xhr.setRequestHeader('Content-Type', 'application/json');
//         xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));  // Include the CSRF token

//         xhr.onload = function () {
//             if (xhr.status >= 200 && xhr.status < 300) {
//                 var response = JSON.parse(xhr.responseText);
//                 console.log('Request successful:', response);
//             } else {
//                 console.error('Request failed with status:', xhr.status);
//             }
//         };

//         xhr.onerror = function () {
//             console.error('Network error occurred');
//         };

//         xhr.send(JSON.stringify({}));
//     });
// });

// function getCookie(name) {
//     var cookieValue = null;
//     if (document.cookie && document.cookie !== '') {
//         var cookies = document.cookie.split(';');
//         for (var i = 0; i < cookies.length; i++) {
//             var cookie = cookies[i].trim();
//             // Check if this cookie name begins with the given name
//             if (cookie.substring(0, name.length + 1) === (name + '=')) {
//                 cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
//                 break;
//             }
//         }
//     }
//     return cookieValue;
// }
