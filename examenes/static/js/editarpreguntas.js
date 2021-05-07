$(document).ready(function(){

    var ultima = parseInt($("#opcionesoculto").text())
    console.log(ultima);

    jQuery(document).on('click',"#agregaropcion", function(data) {
        // id = data.target.id.replace('addoption','')
        // ultima_opcion= parseInt($('#pregunta'+ id + ' input:last').attr('id').slice(-1))

        ultima = ultima + 1
        
        
        if (ultima >=7) {
            $("#agregaropcion").attr({
                'disabled': true
            })
        }
        $("#caja-opciones")
        .append(
            `<div class="row mb-2  m-0" id="cont-`+(ultima)+`">
                <div class="col-md-2  d-flex justify-content-center align-items-center">
                    <div class="form-check form-switch d-flex justify-content-center ">
                    <input class="form-check-input" type="checkbox" value="1"
                    id="correcta`+(ultima)+`" name="correcta`+(ultima)+`">
                    </div>
                </div>
                <div class="col-md-9 ps-0">
                    <textarea type="text" class="form-control" rows="2" name="opcion`+(ultima)+`" id="opcion`+(ultima)+`" required></textarea>
                </div>
                        
                <div class="col-md-1 d-flex justify-content-center align-items-center border rounded my-1">
                    <button type="button" class="btn-close opcion" aria-label="Close"></button>
                </div>
            
            `
        )
    })


    jQuery(document).on('click', ".btn-close.opcion", function (event) {
        jQuery(this).closest('.row.mb-2').remove()
        console.log(ultima);
        ultima = ultima - 1
        if (ultima <6){
            $("#agregaropcion").attr({
                'disabled': false
            })
        }


    });

    jQuery(document).on('click', ".form-check-input", function (event) {
        console.log("entra en la funcion");
        $('.form-check-input').not(this).prop('checked', false);
    });

    $('#enviar').click(function () {
        var atLeastOneIsChecked = false;
        $('input:checkbox').each(function () {
          if ($(this).is(':checked')) {
            atLeastOneIsChecked = true;
            // Stop .each from processing any more items
            return false;
          }
        });
        if (!atLeastOneIsChecked) {
            alert("Debe haber una respuesta correcta")
            return false
        }
        // Do something with atLeastOneIsChecked
      });

})