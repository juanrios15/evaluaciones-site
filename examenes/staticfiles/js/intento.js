$(document).ready(function()
    {   
        var x = new Date($("#hora_inicio").text())
        var y = new Date($("#hora_fin").text())
        
        setInterval(function() {
            var tiempo_restante = (y - new Date())/1000
            console.log(tiempo_restante);
            mins = Math.floor(tiempo_restante/60)
            secs = parseInt(tiempo_restante%60)
        
            if (secs <10) {
                $('#timer').text(mins + ":0"+ secs);

            }else {

                $('#timer').text(mins + ":"+ secs);
            }
            if (mins == 0 && secs == 0) {
                $("#enviarform")[0].click()
            }

        }, 1000);

        
    })