const cart_element = document.querySelector("#cart");
const confirm_button = cart_element.querySelector("button");
const cart_products_count = cart_element.querySelector("p");

const product_cards_container = document.getElementById("product-cards-container");
const product_card = product_cards_container.querySelectorAll('.product-card');

let localCart = localStorage.getItem("cart")
if (localCart){
  let fineArray = JSON.parse(localCart)
  fineArray.forEach(function(element){
    cart_products_count.textContent += element + " "
  })
}

confirm_button.addEventListener("click", confirm_order);
const cart = []
product_card.forEach(function(card){
  let button = card.querySelector('button');
  button.addEventListener('click', add_to_cart);
});

function add_to_cart(){
  let currentId = this.id
  cart.push(currentId)
  cart_products_count.textContent += currentId + " ";
  console.log(JSON.stringify(cart))
  localStorage.setItem("cart", JSON.stringify(cart))
}

function confirm_order(){
  window.location.href = 'shop/order'
  // const url = "http://localhost:8000/shop123";
  // const data = {
  //   order:cart
  // }
  // const options = {
  //   method:"POST",
  //   headers:{
  //     'Content-Type': 'application/json'
  //   },
  //   body: JSON.stringify(data)
  // };

  // console.log(JSON.stringify(data))
  
  // fetch(url,options)
  //   .then(response => {
  //     if (!response.ok){
  //       throw new Error('Network response was not ok');
  //     }
  //     return response.json();
  //   }).then(data => {
  //     console.log('Server response:', data);
  //   }).catch(error => {
  //     console.error('Error: ', error);
  //   });
}