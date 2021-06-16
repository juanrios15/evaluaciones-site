

function notificaciones() { 

    axios.get('/api/notificaciones/usuario').then(
    
        function(response){
            var data = response.data
            $('#lista-notificaciones').empty()
            console.log(data);
            for (let index = 0; index < data.length; index++) {
                if (data[index].usuario_notificacion.foto == null) 
                {
                    $('#lista-notificaciones')
                    .append(
                        `<div class="row align-items-center">
                        <div class="col-md-1">
                            <a href="/detalleusuario/`+data[index].usuario_notificacion.slug+`">
                                <img class="d-block rounded mb-1 " style="height: 35px; width: 35px;" src="/static/img/no-image.png" alt="">
                            </a>
                        </div>
                        <div class="col-md-10 text-start">
                            `+data[index].mensaje+`
                        </div>
                        <div class="col-md-1">
                            <button type="button" value="`+data[index].id+`" class="btn-close opc border rounded shadow-sm p-1" aria-label="Close"></button>
                        </div>
                        <hr class="my-2">
                    </div>`
                    );

                } else {
                    $('#lista-notificaciones')
                    .append(
                        `<div class="row align-items-center">
                        <div class="col-md-1">
                            <a href="/detalleusuario/`+data[index].usuario_notificacion.slug+`">
                                <img class="d-block rounded mb-1 " style="height: 35px; width: 35px;" src="`+data[index].usuario_notificacion.foto+`" alt="">
                            </a>
                        </div>
                        <div class="col-md-10 text-start">
                            `+data[index].mensaje+`
                        </div>
                        <div class="col-md-1">
                            <button type="button" value="`+data[index].id+`"  class="btn-close opc border rounded shadow-sm p-1 " aria-label="Close"></button>
                            
                        </div>
                        <hr class="my-2">
                    </div>`
                    );
                };
                
            }

        })

    }

jQuery(document).on('click', ".btn-close.opc", function (event) {
    var id = jQuery(this).val();
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    axios.delete('/api/eliminarnoti/'+id,
    {
        headers: {
             'X-CSRFTOKEN': csrftoken,
         },
    },).then(
        function(response){
            console.log("Eliminado con exito");
        })
    
    jQuery(this).closest('.row').remove()
});
