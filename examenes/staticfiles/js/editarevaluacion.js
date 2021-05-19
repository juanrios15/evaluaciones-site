$(document).ready(function(){

    //init data

    var categoriax = $("#catoculto").text()
    var subcategoriax = $("#suboculto").text()
    var cant_preguntas = parseInt($("#preguntasoculto").text()) 
    console.log(cant_preguntas);
    if (cant_preguntas>60) {
        cant_preguntas = 60
        mensaje = "Maximo 60 preguntas por intento"
    }else {
        mensaje = "No tienes tantas preguntas elaboradas para esta evaluación, tienes que hacer más"
    }
    console.log($("#listasubcategoria").text());

    
    axios.get('http://127.0.0.1:8000/api/categorias/list').then(
        
        function(response){
            var y = response.data
            console.log(y);
            for (var i = 0; i < y.length; i++) {
                    if (categoriax == y[i].nombre) {
                        $('#listacategoria').append('<option value="' + y[i].nombre+ '" selected>' + y[i].nombre + '</option>');
                    }else {
                        $('#listacategoria').append('<option value="' + y[i].nombre+ '">' + y[i].nombre + '</option>');
                    }
                }
            for (var i = 0; i < y.length; i++) {
                if (categoriax === y[i].nombre ) {
                    $('#listasubcategoria').append('<option value="">' + "Seleccione una opción" +'</option>');
                    for (var j=0;j<y[i].subcategoria.length;j++) {
                        if (subcategoriax == y[i].subcategoria[j].nombre) {
                            $('#listasubcategoria').append('<option value="' + y[i].subcategoria[j].id+ '" selected>' + y[i].subcategoria[j].nombre + '</option>');
                        }else {
                            $('#listasubcategoria').append('<option value="' + y[i].subcategoria[j].id+ '">' + y[i].subcategoria[j].nombre + '</option>');
                        }
                    }
                }
            }
            var subcategoria = []
            $("#listacategoria").click( function () {
                $('#listasubcategoria')
                .find('option')
                .remove()
                .end()
                cat = $("#listacategoria").val()
                for (var i = 0; i < y.length; i++) {
                    if (cat === y[i].nombre ) {
                        $('#listasubcategoria').append('<option value="">' + "Seleccione una opción" +'</option>');
                        for (var j=0;j<y[i].subcategoria.length;j++) {
                            if (subcategoriax == y[i].subcategoria[j]) {
                                $('#listasubcategoria').append('<option value="' + y[i].subcategoria[j]+ '" selected>' + y[i].subcategoria[j] + '</option>');
                            }else {
                                $('#listasubcategoria').append('<option value="' + y[i].subcategoria[j]+ '">' + y[i].subcategoria[j] + '</option>');
                            }
                        }
                    }
                }
            }
            )

        })
    
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
        
        $("#formupdate").validate()
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
            max:cant_preguntas,
            messages: {

                min: jQuery.validator.format("Minimo 5 preguntas por intento"),
                max: jQuery.validator.format(mensaje)
              }
          }),
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


})