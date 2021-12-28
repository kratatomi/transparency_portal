// import { ethers } from "https://cdn.ethers.io/lib/ethers-5.2.esm.min.js";

let provider;
let accounts;

let accountAddress = "";
let signer;

function login() {
  console.log("oh hey there");

  // signer.signMessage("hello");

  rightnow = (Date.now() / 1000).toFixed(0);
  sortanow = rightnow - (rightnow % 600);

  signer
    .signMessage(
      "Signing in to transparency.smartindex.cash at " + sortanow,
      accountAddress,
      "test password!"
    )
    .then((signature) => {
      handleAuth(accountAddress, signature);
    });
}

function handleAuth(accountAddress, signature) {
  console.log(accountAddress);
  console.log(signature);

  fetch("login", {
    method: "post",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify([accountAddress, signature]),
  })
    .then((response) => {
      return response.json();
    })
    .then((data) => {
      console.log(data);
    });
}

ethereum.enable().then(function () {
  provider = new ethers.providers.Web3Provider(web3.currentProvider);

  provider.getNetwork().then(function (result) {
    if (result["chainId"] != 10000) {
      document.getElementById("msg").textContent = "Switch to SmartBCH!";
    } else {
      // okay, confirmed we're on mainnet

      provider.listAccounts().then(async function (result) {
        console.log(result);
        accountAddress = result[0]; // getting uesrs publickey

        // contract address and contract abi is used to create the contract instance
        const contractAddress = "0xF05bD3d7709980f60CD5206BddFFA8553176dd29";
        const contractABI = [
          // balanceOf
          {
            constant: true,
            inputs: [{ name: "_owner", type: "address" }],
            name: "balanceOf",
            outputs: [{ name: "balance", type: "uint256" }],
            type: "function",
          },
          // decimals
          {
            constant: true,
            inputs: [],
            name: "decimals",
            outputs: [{ name: "", type: "uint8" }],
            type: "function",
          },
        ];

        // creating contract instance
        const contract = new ethers.Contract(
          contractAddress,
          contractABI,
          provider
        );

        // getting the contract decimals and balance
        const decimals = await contract.decimals();
        let balance = await contract.balanceOf(accountAddress);
        balance = parseFloat(ethers.utils.formatUnits(balance, decimals));

        if (balance < 5000) {
          // if SIDX  balance < 5000, insufficient balance
          document.getElementById("msg").textContent =
            "You need at least 5000 SIDX tokens to submit a proposal";
        } else {
          // else allow user to submit proposal
          const submitProposalButton =
            document.getElementById("login");
          submitProposalButton.disabled = false;
          signer = provider.getSigner();
        }
      });
    }
  });
});