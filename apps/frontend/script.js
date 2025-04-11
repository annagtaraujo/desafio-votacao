let num1, num2;

function gerarDesafio() {
  num1 = Math.floor(Math.random() * 10) + 1;
  num2 = Math.floor(Math.random() * 10) + 1;
  document.getElementById("desafio").innerText = `Quanto é ${num1} + ${num2}?`;
}

function votar(opcao) {
  const resposta = parseInt(document.getElementById("resposta").value);
  if (resposta !== num1 + num2) {
    alert("Resposta incorreta. Tente novamente.");
    gerarDesafio();
    return;
  }

  fetch("http://backend-service:5000/votar", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ opcao })
  })
  .then(res => res.json())
  .then(data => {
    document.getElementById("mensagem").innerText = data.mensagem;
    gerarDesafio(); // novo desafio após voto
    document.getElementById("resposta").value = "";
  })
  .catch(err => console.error(err));
}

gerarDesafio(); // gera logo ao carregar
