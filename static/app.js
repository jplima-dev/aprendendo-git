// ===============================
// ABAS
// ===============================
function mostrarAba(nomeAba) {
    document.querySelectorAll(".aba").forEach(aba => {
        aba.style.display = "none";
    });

    document.getElementById(nomeAba).style.display = "block";
}


// ===============================
// MODAL
// ===============================
function abrirModal(tipo) {
    const overlay = document.getElementById("modalOverlay");
    const conteudo = document.getElementById("modalConteudo");

    overlay.style.display = "flex";

    if (tipo === "morador") {
        conteudo.innerHTML = `
            <h2>Novo Morador</h2>

            <input id="nome" placeholder="Nome"><br><br>
            <input id="email" placeholder="Email"><br><br>
            <input id="telefone" placeholder="Telefone"><br><br>
            <input id="apartamento" placeholder="Apartamento"><br><br>

            <button onclick="salvarMorador(); fecharModal();">
                Salvar
            </button>
        `;
    }

    if (tipo === "aviso") {
        conteudo.innerHTML = `
            <h2>Novo Aviso</h2>

            <input id="novoAviso" placeholder="Digite o aviso"><br><br>

            <button onclick="salvarAviso(); fecharModal();">
                Salvar
            </button>
        `;
    }

    if (tipo === "aluguel") {
        conteudo.innerHTML = `
            <h2>Novo Aluguel</h2>

            <input id="aluguelApartamento" placeholder="Apartamento"><br><br>
            <input id="aluguelValor" placeholder="Valor"><br><br>
            <input id="aluguelVencimento" type="date"><br><br>

            <button onclick="salvarAluguel(); fecharModal();">
                Salvar
            </button>
        `;
    }

    if (tipo === "boleto") {
        conteudo.innerHTML = `
            <h2>Novo Boleto</h2>

            <input id="boletoApartamento" placeholder="Apartamento"><br><br>
            <input id="boletoValor" placeholder="Valor"><br><br>

            <button onclick="gerarBoleto(); fecharModal();">
                Salvar
            </button>
        `;
    }
}

function fecharModal() {
    document.getElementById("modalOverlay").style.display = "none";
}



// ===============================
// MORADORES
// ===============================
async function salvarMorador() {
    const nome = document.getElementById("nome").value.trim();
    const email = document.getElementById("email").value.trim();
    const telefone = document.getElementById("telefone").value.trim();
    const apartamento = document.getElementById("apartamento").value.trim();

    if (!nome || !email || !apartamento) {
        alert("Nome, Email e Apartamento são obrigatórios.");
        return;
    }

    await fetch("/api/moradores", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            nome,
            email,
            telefone,
            apartamento
        })
    });

    carregarMoradores();
}


async function carregarMoradores() {
    const lista = document.getElementById("listaMoradores");

    const res = await fetch("/api/moradores");
    const moradores = await res.json();

    lista.innerHTML = "";

    moradores.forEach(morador => {
        lista.innerHTML += `
            <tr>
                <td>${morador.nome}</td>
                <td>${morador.email}</td>
                <td>${morador.telefone || ""}</td>
                <td>${morador.apartamento}</td>
                <td>
                    <button onclick="editarMorador(${morador.id})">Editar</button>
                    <button onclick="excluirMorador(${morador.id})">Excluir</button>
                </td>
            </tr>
        `;
    });
}


async function excluirMorador(id) {
    await fetch(`/api/moradores/${id}`, {
        method: "DELETE"
    });

    carregarMoradores();
}


async function editarMorador(id) {
    const nome = prompt("Nome:");
    const email = prompt("Email:");
    const telefone = prompt("Telefone:");
    const apartamento = prompt("Apartamento:");

    if (!nome || !email || !apartamento) return;

    await fetch(`/api/moradores/${id}`, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            nome,
            email,
            telefone,
            apartamento
        })
    });

    carregarMoradores();
}



// ===============================
// AVISOS
// ===============================
function salvarAviso() {
    const texto = document.getElementById("novoAviso").value.trim();

    if (!texto) return;

    let avisos =
        JSON.parse(localStorage.getItem("avisos")) || [];

    avisos.push(texto);

    localStorage.setItem(
        "avisos",
        JSON.stringify(avisos)
    );

    carregarAvisos();
}


function carregarAvisos() {
    const lista = document.getElementById("listaAvisos");

    let avisos =
        JSON.parse(localStorage.getItem("avisos")) || [];

    lista.innerHTML = "";

    avisos.forEach((aviso, index) => {
        lista.innerHTML += `
            <li>
                ${aviso}
                <button onclick="editarAviso(${index})">Editar</button>
                <button onclick="removerAviso(${index})">Excluir</button>
            </li>
        `;
    });
}


function editarAviso(index) {
    let avisos =
        JSON.parse(localStorage.getItem("avisos")) || [];

    const novo = prompt("Editar aviso:", avisos[index]);

    if (!novo) return;

    avisos[index] = novo;

    localStorage.setItem(
        "avisos",
        JSON.stringify(avisos)
    );

    carregarAvisos();
}


function removerAviso(index) {
    let avisos =
        JSON.parse(localStorage.getItem("avisos")) || [];

    avisos.splice(index, 1);

    localStorage.setItem(
        "avisos",
        JSON.stringify(avisos)
    );

    carregarAvisos();
}



// ===============================
// ALUGUEL
// ===============================
function salvarAluguel() {
    const apartamento =
        document.getElementById("aluguelApartamento").value;

    const valor =
        document.getElementById("aluguelValor").value;

    const vencimento =
        document.getElementById("aluguelVencimento").value;

    if (!apartamento || !valor || !vencimento) return;

    let alugueis =
        JSON.parse(localStorage.getItem("alugueis")) || [];

    alugueis.push({
        apartamento,
        valor,
        vencimento
    });

    localStorage.setItem(
        "alugueis",
        JSON.stringify(alugueis)
    );

    carregarAlugueis();
}


function carregarAlugueis() {
    const lista = document.getElementById("listaAlugueis");

    let alugueis =
        JSON.parse(localStorage.getItem("alugueis")) || [];

    lista.innerHTML = "";

    alugueis.forEach((aluguel, index) => {
        lista.innerHTML += `
            <tr>
                <td>${aluguel.apartamento}</td>
                <td>R$ ${aluguel.valor}</td>
                <td>${aluguel.vencimento}</td>
                <td>
                    <button onclick="editarAluguel(${index})">Editar</button>
                    <button onclick="removerAluguel(${index})">Excluir</button>
                </td>
            </tr>
        `;
    });
}


function editarAluguel(index) {
    let alugueis =
        JSON.parse(localStorage.getItem("alugueis")) || [];

    const aluguel = alugueis[index];

    aluguel.apartamento =
        prompt("Apartamento:", aluguel.apartamento);

    aluguel.valor =
        prompt("Valor:", aluguel.valor);

    aluguel.vencimento =
        prompt("Vencimento:", aluguel.vencimento);

    localStorage.setItem(
        "alugueis",
        JSON.stringify(alugueis)
    );

    carregarAlugueis();
}


function removerAluguel(index) {
    let alugueis =
        JSON.parse(localStorage.getItem("alugueis")) || [];

    alugueis.splice(index, 1);

    localStorage.setItem(
        "alugueis",
        JSON.stringify(alugueis)
    );

    carregarAlugueis();
}



// ===============================
// BOLETOS
// ===============================
function gerarBoleto() {
    const apartamento =
        document.getElementById("boletoApartamento").value;

    const valor =
        document.getElementById("boletoValor").value;

    let boletos =
        JSON.parse(localStorage.getItem("boletos")) || [];

    boletos.push({
        apartamento,
        valor
    });

    localStorage.setItem(
        "boletos",
        JSON.stringify(boletos)
    );

    carregarBoletos();
}


function carregarBoletos() {
    const lista = document.getElementById("listaBoletos");

    let boletos =
        JSON.parse(localStorage.getItem("boletos")) || [];

    lista.innerHTML = "";

    boletos.forEach((boleto, index) => {
        lista.innerHTML += `
            <li>
                Apartamento ${boleto.apartamento} — R$ ${boleto.valor}
                <button onclick="editarBoleto(${index})">Editar</button>
                <button onclick="removerBoleto(${index})">Excluir</button>
            </li>
        `;
    });
}


function editarBoleto(index) {
    let boletos =
        JSON.parse(localStorage.getItem("boletos")) || [];

    boletos[index].apartamento =
        prompt("Apartamento:", boletos[index].apartamento);

    boletos[index].valor =
        prompt("Valor:", boletos[index].valor);

    localStorage.setItem(
        "boletos",
        JSON.stringify(boletos)
    );

    carregarBoletos();
}


function removerBoleto(index) {
    let boletos =
        JSON.parse(localStorage.getItem("boletos")) || [];

    boletos.splice(index, 1);

    localStorage.setItem(
        "boletos",
        JSON.stringify(boletos)
    );

    carregarBoletos();
}



// ===============================
// INICIAR
// ===============================
window.addEventListener("DOMContentLoaded", () => {
    mostrarAba("moradores");

    carregarMoradores();
    carregarAvisos();
    carregarAlugueis();
    carregarBoletos();
});