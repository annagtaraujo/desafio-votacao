function votar(opcao) {
    const token = grecaptcha.getResponse();
    if (!token) {
      alert("Por favor, confirme que você é humano.");
      return;
    }
  
    fetch("http://backend-service:5000/votar", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ opcao, token })
    })
    .then(res => res.json())
    .then(data => {
      document.getElementById("mensagem").innerText = data.mensagem;
      grecaptcha.reset();
    })
    .catch(err => console.error(err));
  }
  