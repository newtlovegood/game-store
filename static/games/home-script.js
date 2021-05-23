// (B) MESSAGE BAR
function mbar (msg, css) {
  // (B1) CREATE BAR
  var bar = document.createElement("div");
  bar.innerHTML = msg;
  if (css === 'info') { bar.classList.add('alert', 'alert-dark', 'alert-success', 'text-center' ); }
  if (css === 'err') { bar.classList.add('alert', 'alert-dark', 'alert-danger', 'text-center' ); }

  // (B2) CLICK TO CLOSE
  bar.onclick = function(){
    document.getElementById("mbar").removeChild(this);
  };

  // (B3) APPEND TO CONTAINER
  if (document.getElementById('mbar').children.length > 0) {
    document.getElementById("mbar").removeChild(document.getElementById("mbar").children[0]);
    setTimeout(function () {document.getElementById("mbar").appendChild(bar)}, 100);
    console.log('ok')

  } else {
    document.getElementById("mbar").appendChild(bar);
  }
}


// CURRENT ORDER
// let itemQty = document.getElementById('cart-item-qty').innerText;


// $('.cart-plus').each(function (){
//   $(this).on('click', function (){
//       let valueCount = $(this).siblings()[1].value;
//       valueCount ++;
//       $(this).siblings()[1].value = valueCount;
//
//       if ($(this).siblings()[1].value > 0) {
//         $(this).siblings()[0].removeAttribute('disabled');
//       }
//   })
// })

// $('.cart-minus').each(function (){
//   // if added qty === 1 then minus is disabled
//   if ($(this).siblings()[0].value == 1) {
//     this.setAttribute('disabled', 'disabled');
//   }
//
//   // click event
//   $(this).on('click', function (){
//     // reduce by 1
//     valueCount = $(this).siblings()[0].value;
//     valueCount --;
//     $(this).siblings()[0].value = valueCount;
//
//     // disable if less than 2
//     if (valueCount == 1) {
//       this.setAttribute('disabled', 'disabled');
//     }
//     // ajax call
//     $.ajax({
//                 type: 'POST',
//                 url: '{% url "order:add-to-cart" %}',
//                 data: {
//                     gameId: $('#cart-minus').data('index'),
//                     gameQty: $('#cart-item-qty').val(),
//                     csrfmiddlewaretoken: "{{ csrf_token }}",
//                     action: 'post',
//                 },
//                 success: function (json) {
//                     document.getElementById('cart-qty').innerHTML = json.qty;
//                 },
//                 error: function (xhr, errmsg, err) {
//                 }
//             });
//
//   })
// })