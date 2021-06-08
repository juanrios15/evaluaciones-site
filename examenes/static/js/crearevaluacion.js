
$(document).ready(function(){

    //init data

    axios.get('api/categorias/list').then(
        
        function(response){
            var y = response.data
            console.log(y);
            for (var i = 0; i < y.length; i++) {
                    $('#listacategoria').append('<option value="' + y[i].nombre+ '">' + y[i].nombre + '</option>');
                }

            var subcategoria = []
            $("#listacategoria").change( function () {
                $('#listasubcategoria')
                .find('option')
                .remove()
                .end()
                cat = $("#listacategoria").val()
                
                for (var i = 0; i < y.length; i++) {
                    if (cat === y[i].nombre ) {
                        $('#listasubcategoria').append('<option value="">' + "Seleccione una opción" +'</option>');
                        for (var j=0;j<y[i].subcategoria.length;j++) {
                            $('#listasubcategoria').append('<option value="' + y[i].subcategoria[j].nombre+ '">' + y[i].subcategoria[j].nombre + '</option>');
                        }
                    }
                }
            }
            )
        })
        jQuery(document).on('click',"button[id^='addoption']", function(data) {
            id = data.target.id.replace('addoption','')
            ultima_opcion= parseInt($('#pregunta'+ id + ' input:last').attr('id').slice(-1))
            
            if (ultima_opcion >=6) {
                $("#addoption"+id).attr({
                    'disabled': true,
                    'style': 'background-color: gray'
                })
            }
            $("#pregunta"+id)
            .append(
                `<div class="row justify-content-center">
                <div class="col-2 d-flex align-items-center justify-content-center">
                    <div class="form-check mt-3 form-switch d-flex justify-content-center">
                        <input class="form-check-input pregunta`+id+`" type="checkbox"  value="1" id="pregunta-`+id+`-opcion-`+(ultima_opcion+1)+`-correcta" name="pregunta-`+id+`-opcion-`+(ultima_opcion+1)+`-correcta">
                      </div>
                </div>
                <div class="col-9">
                    <label for="opcion-`+(ultima_opcion+1)+`" class="form-label">Opción</label>
                    <input type="text" class="form-control" id="pregunta-`+id+`-opcion-`+(ultima_opcion+1)+`" name="pregunta-`+id+`-opcion-`+(ultima_opcion+1)+`" placeholder="" required>
                </div>
                <div class="col-1 d-flex justify-content-center align-items-end pb-2 px-0">
                    <button type="button" class="btn-close opc border rounded shadow-sm p-1 " aria-label="Close"></button>
                </div>
            </div>`
            )
        })
        $("#addpregunta").click( function() {

            ultima_pregunta = parseInt($('#questions button:last').attr('id').replace( /^\D+/g, ''))
            console.log(ultima_pregunta);
            $("#questions")
            .append(
                `
                <div class="mb-3 col-md-12 col-lg-6">
                    <div id="pregunta`+(ultima_pregunta+1)+`">
                        <div class="row">
                            <div class="col-md-10">
                            <label for="pregunta-`+(ultima_pregunta+1)+`" class="form-label">Pregunta</label>
                            </div>
                            <div class="col-md-2 text-end ">
                            <button type="button" class="btn-close caja border rounded shadow-sm p-1" aria-label="Close"></button>
                            </div>
                        </div>
                        <textarea class="form-control" id="pregunta-`+(ultima_pregunta+1)+`" name="pregunta-`+(ultima_pregunta+1)+`" rows="3" required></textarea>

                        <div class="row justify-content-center">
                            <div class="col-2 px-0">
                                <div class="mb-2">Correcta?</div>
                                <div class="form-check form-switch d-flex justify-content-center">
                                    <input class="form-check-input pregunta`+(ultima_pregunta+1)+`" type="checkbox" value="1"
                                        id="pregunta-`+(ultima_pregunta+1)+`-opcion-1-correcta" name="pregunta-`+(ultima_pregunta+1)+`-opcion-1-correcta">
                                </div>
                            </div>
                            <div class="col-10">
                                <label for="opcion-1" class="form-label">Opción</label>
                                <input type="text" class="form-control" id="pregunta-`+(ultima_pregunta+1)+`-opcion-1"
                                    name="pregunta-`+(ultima_pregunta+1)+`-opcion-1" placeholder="" required>

                            </div>

                        </div>
                        <div class="row justify-content-center">
                            <div class="col-2 d-flex align-items-center justify-content-center">
                                <div class="form-check mt-3 form-switch d-flex justify-content-center">
                                    <input class="form-check-input pregunta`+(ultima_pregunta+1)+`" type="checkbox" value="1"
                                        id="pregunta-`+(ultima_pregunta+1)+`-opcion-2-correcta" name="pregunta-`+(ultima_pregunta+1)+`-opcion-2-correcta">
                                </div>
                            </div>
                            <div class="col-10">
                                <label for="opcion-1" class="form-label">Opción</label>
                                <input type="text" class="form-control" id="pregunta-`+(ultima_pregunta+1)+`-opcion-2"
                                    name="pregunta-`+(ultima_pregunta+1)+`-opcion-2" placeholder="" required>
                            </div>
                        </div>
                    </div>
                    <button type="button" class="btn rounded border shadow mt-2" id="addoption`+(ultima_pregunta+1)+`">Agregar opción</button>
                </div>
                `
            )

        })

        jQuery(document).on('click', "input[class^='form-check-input']", function (event) {

            id = event.target.id.match(/\d+/)

            $('.form-check-input.pregunta'+id[0]).not(this).prop('checked', false);
        });
        jQuery(document).on('click', ".btn-close.opc", function (event) {
            jQuery(this).closest('.row').remove()
        });
        jQuery(document).on('click', ".btn-close.caja", function (event) {
            jQuery(this).closest('.mb-3.col-md-6').remove()
        });
        

        //Modificar la imagen automaticamente
        function readURL(input) {
            if (input.files && input.files[0]) {
                var reader = new FileReader();
    
                reader.onload = function (e) {
                    $('#mostrarimg').attr('src', e.target.result);
                    console.log("holaaa");
                }
    
                reader.readAsDataURL(input.files[0]);
            }
        }
    
        $("#inputimg").change(function(){
            readURL(this);
        });



        var validation = true
        //TODO:  aca se debe modificar el validate para hacer las validaciones de cada uno de los espacios
        $("#form1").validate()
        $("#enviarevaluacion").click( function(data) {
            
            if($("#form1").valid()) {
                
                $("div[id^='pregunta']").each( function(data) {
                    
                    if($(this).find(':checkbox:checked').length === 0) {
                        alert("Todas las preguntas deben tener una respuesta correcta!");
                        validation = false
                        return false
                    }
                    validation = true
                    // var atLeastOneIsChecked =$(this).is(':checked');
                    // if(!atLeastOneIsChecked) {
                        //     return false;
                        //   }
                    }
                    )
                    var cant_pre= $("#id_cant_preguntas").val(); 
                    var numItems = $("div[id^='pregunta']").length
                    console.log(cant_pre);
                    console.log(numItems);
                    if(cant_pre>numItems) {
                        validation = false
                        alert("Más preguntas que # de preguntas por intento");
                    }
                    
                if (validation) {
                    return true
                }else {
                    return false
                }
            }
            
            
            
        })
        $.validator.messages.required = 'Campo  requerido';   

        $("#id_puntaje_minimo").rules( "add", {
            min: 60,
            max:100,
            messages: {
                
                min: jQuery.validator.format("Puntaje minimo de 60"),
                max: jQuery.validator.format("Puntaje maximo de 100")
              }
          });
        $("#id_nombre").rules( "add", {
            minlength: 10,
            messages: {
                minlength: jQuery.validator.format("Minimo 10 caracteres. Entre mejor nombres tu evaluación más facil será de encontrar")
              }
          });
        $("#id_cant_preguntas").rules( "add", {
            min: 5,
            max:60,
            messages: {

                min: jQuery.validator.format("Minimo 5 preguntas por intento"),
                max: jQuery.validator.format("Maximo 60 preguntas por intento")
              }
          });
        $("#id_intentos_permitidos").rules( "add", {
            min: 1,
            max:5,
            messages: {

                min: jQuery.validator.format("Minimo 1 intento"),
                max: jQuery.validator.format("Maximo 5 intentos permitidos")
              }
          });
        $("#id_tiempo_limite").rules( "add", {
            min: 1,
            max:120,
            messages: {

                min: jQuery.validator.format("Minimo 1 minuto por intento"),
                max: jQuery.validator.format("Maximo 120 minutos por intento")
              }
          });
        $("#id_dificultad").rules( "add", {
            min: 1,
            max:10,
            messages: {

                min: jQuery.validator.format("Minimo dificultad de 1"),
                max: jQuery.validator.format("Maximo dificultad de 10")
              }
          });
        
    
    });
