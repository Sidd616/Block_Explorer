// Function to retrieve and populate block data from sessionStorage
function retrieveAndPopulateData() {
      // Iterate over all blocks to retrieve and populate their data
      document.querySelectorAll(".block-data").forEach(function(textarea) {
          var blockDataId = textarea.id.split("-")[2];
          var storedData = sessionStorage.getItem("blockData-" + blockDataId);
          if (storedData !== null) {
              textarea.value = storedData;
          }
      });
  }

  // Function to populate block data from sessionStorage
function populateBlockDataFromStorage() {
      // Trigger the function on change event of block data textareas
      document.querySelectorAll(".block-data").forEach(function(textarea) {
          textarea.addEventListener("change", retrieveAndPopulateData);
      });

      // Trigger the function on click event of mine buttons
      document.querySelectorAll(".mineBtn").forEach(function(button) {
          button.addEventListener("click", retrieveAndPopulateData);
      });

      // Call the function initially to populate block data when the page loads
      retrieveAndPopulateData();
  }



document.getElementById("createBlockBtn").addEventListener("click", function() {
      fetch("/create_block", {
          method: "POST",
          headers: {
              "Content-Type": "application/json"
          },
          body: JSON.stringify({
              // You can send any data you need for block creation
          })
      })
      .then(response => {
          if (response.ok) {
              return response.text();
          } else {
              console.error("Error:", response.statusText);
              throw new Error(response.statusText);
          }
      })
      .then(data => {
          document.getElementById("blockchain").innerHTML += data;
          retrieveAndPopulateData();
          if (document.querySelectorAll(".block").length > 0) {
              document.getElementById("createBlockBtn").innerText = "Add Block";
              document.getElementById("resetBtn").style.display = "inline";
          }
      })
      .catch(error => {
          console.error("Error:", error);
      });
  });



function mineBlock(blockNumber, blockDataId) {
    // Retrieve the value of the textarea using the provided blockDataId
    var blockData = document.getElementById("block-data-" + blockDataId).value;

    fetch("/store_data", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            // Include the nonce in the request body
            body: "block_number=" + blockNumber + "&data=" + encodeURIComponent(blockData) + "&nonce=" + encodeURIComponent(blockDataId)
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            }
            throw new Error("Network response was not ok.");
        })
        .then(data => {
            // Check if the response indicates that the data is already up to date
            if (data === "Block with the provided nonce not found") {
                console.log("Block with the provided nonce not found");
                return; // Exit the function without making any further changes
            }

            if (data === "block up to date") {
                  console.log("block was up to date");
                  return; // Exit the function without making any further changes
              }

            // Get the <span> element with the hash text
            var hashSpan = document.querySelector("#hash-" + blockDataId + " .hash-text");
            // Replace the inner text of the <span> with the new hash
            hashSpan.textContent = data.hash;

            // Get the <span> element with the hash text
            var txRootSpan = document.querySelector("#txhash-" + blockDataId + " .hash-text");
            // Replace the inner text of the <span> with the new tx_root
            txRootSpan.textContent = data.tx_root;

            // Get the <span> element with the hash text
            var prevSpan = document.querySelector("#prehash-" + blockDataId + " .hash-text");
            // Replace the inner text of the <span> with the new prev hash
            prevSpan.textContent = data.prev;

            var textarea = document.getElementById("block-data-" + blockDataId);
            textarea.value = data.data;

            // Store the updated data in sessionStorage
            sessionStorage.setItem("blockData-" + blockDataId, data.data);

            // Select all divs inside <div id="blockchain"> with id="main-{blockNumber}"
            var blockchainDiv = document.getElementById("blockchain");
            var blockDivs = blockchainDiv.querySelectorAll("[id^='main-']");

            // Loop through the block divs and update their classes
            blockDivs.forEach(function (blockDiv) {
                // Get the block number from the id
                var idParts = blockDiv.id.split("-");
                var currentBlockNumber = parseInt(idParts[1]);

                // Check if the block number is greater than the current block number
                if (currentBlockNumber > blockNumber) {
                    // Change the class name of the block div
                    blockDiv.className = "block-not";
                }
                else{
                    // Change the class name of the block div
                    blockDiv.className = "block";
                }
            });
        })
        .catch(error => {
            console.error("There was a problem with the fetch operation:", error);
        });
}





  document.getElementById("resetBtn").addEventListener("click", function() {
      fetch("/reset_block_number", {
          method: "POST"
      })
      .then(response => {
          if (response.ok) {
              console.log("Block number reset successfully");
          } else {
              console.error("Error:", response.statusText);
          }
      })
      .catch(error => {
          console.error("Error:", error);
      });
  });




  document.getElementById("resetBtn").addEventListener("click", function() {
      document.getElementById("blockchain").innerHTML = "";
      document.getElementById("createBlockBtn").innerText = "Create your First Block";
      document.getElementById("resetBtn").style.display = "none";
  });





  // Call populateBlockDataFromStorage when the page loads
  window.onload = populateBlockDataFromStorage();

