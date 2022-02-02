let provider;
let accounts;

let accountAddress = "";
let signer;

function login() {

  rightnow = (Date.now() / 1000).toFixed(0);
  sortanow = rightnow - (rightnow % 600);

  signer
    .signMessage(
      "Signing in to transparency.smartindex.cash at " + sortanow
    )
    .then((signature) => {
      handleAuth(accountAddress, signature);
    });
}

async function handleAuth(accountAddress, signature) {
  console.log(accountAddress);
  console.log(signature);

  const response = await fetch("login", {
    method: "post",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify([accountAddress, signature]),
  });


  if (response.ok && response.redirected) {
       window.location.href = response.url;
  }
}

ethereum.request({method: 'eth_requestAccounts'}).then(async function (accounts) {
  provider = new ethers.providers.Web3Provider(ethereum);

  const network = await provider.getNetwork();
  if (network["chainId"] !== 10000) {
    document.getElementById("msg").textContent = "Switch to SmartBCH!";
    return;
  }

  // okay, confirmed we're on mainnet
  console.log(accounts);
  accountAddress = ethers.utils.getAddress(accounts[0]); // getting users publickey

  // allow user to log in
  const submitProposalButton =
   document.getElementById("login");
  submitProposalButton.disabled = false;
  signer = provider.getSigner();

});