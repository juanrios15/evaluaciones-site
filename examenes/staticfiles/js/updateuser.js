$(document).ready(function(){

    var x = $("#codoculto").text()
    $("#paisupdate").countrySelect(
        {
            defaultCountry: x,
            preferredCountries: ['co', 'pe', 'mx','ar'],
            responsiveDropdown: false

        }
    );
    $("#pais").countrySelect(
        {
            
            preferredCountries: ['co', 'pe', 'mx','ar'],
            responsiveDropdown: false

        }
    );

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

})