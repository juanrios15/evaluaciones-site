

$(document).ready(function(){

   

    axios.get('api/evaluaciones/list').then(

        function(response){

            lista = []
            for (let index = 0; index < response.data.length; index++) {
                
                lista.push(response.data[index].nombre)
                
            }

            new autoComplete({
                selector: "#autoComplete",
                placeHolder: "Busca evaluaciones...",
                data: {
                    src: lista
                },
                resultsList: {
                    noResults: (list, query) => {
                        // Create "No Results" message element
                        const message = document.createElement("div");

                        // Add class to the created element
                        message.setAttribute("class", "no_result");
                        // Add message text content
                        message.innerHTML = `<span>No se encontraron resultados para "${query}"</span>`;
                        // Append message element to the results list
                        list.appendChild(message);
                    },
                },
                resultItem: {
                    highlight: {
                        render: true
                    }
                },
                onSelection: (feedback) => {

                    // Prepare User's Selected Value
                    const selection = feedback.selection.value;

                    // Replace Input value with the selected value
                    document.querySelector("#autoComplete").value = selection;
                    document.querySelector("#autoComplete").form.submit()

                    // Console log autoComplete data feedback
                    console.log(feedback);
                  }
            });

        }
    )

    $('#autoComplete').keyup(function(e){
        console.log(e.keyCode);
        if(e.keyCode==13) {
            document.querySelector("#autoComplete").form.submit()

        }
      });
})