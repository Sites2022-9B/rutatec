    function sendErrorToDevs(referencia, msg, url) {
        console.log("Desarrollador: Corrige un error presentado en el router:");
        console.log(" url: " + url);
        console.log("ref.: " + referencia);
        console.log("msg : " + msg);
        //alert(referencia);
    }

    function showMsgToastTemp(pos, tiempo, icono, mensaje) {
        const Toast = Swal.mixin({
            toast: true,
            position: pos,
            showConfirmButton: false,
            timer: tiempo,
            timerProgressBar: true,
            didOpen: (toast) => {
                toast.addEventListener('mouseenter', Swal.stopTimer)
                toast.addEventListener('mouseleave', Swal.resumeTimer)
            }
        })
        return Toast.fire({
            icon: icono,
            title: mensaje
        })
    }

    async function showMsg(jqXHR, referencia, url, ret, msg) {
        if (msg == undefined) {
            // En caso de no recibir un msg, considerar el siguiente como predeterminado
            msg = 'Se ha guardado la información de forma correcta !!!';
        }
        if (jqXHR.status == 500) {
            // Enviar mensaje al área de desarrollo
            sendErrorToDevs(referencia, jqXHR.responseText, url);
            await Swal.fire({
                icon: 'error',
                title: 'Ups... se ha presentado un error en el servidor',
                text: 'Informe por favor esta situación al Administrador del sistema',
                // timer: 3500
            }).then((result) => {
                return true;
            });
        } else if (jqXHR.status == 200) {
            await Swal.fire({
                icon: 'success',
                title: 'Operación exitosa...',
                text: msg,
                timer: 3500
            }).then((result) => {
                return true;
            });
        } else if (jqXHR.status == 403) {
            await Swal.fire({
                icon: 'error',
                title: 'No tiene privilegios para ejecutar: ' + url,
                text: "Solicitélos con el administrador del sistema",
            }).then((result) => {
                return true;
            });
        } else if (jqXHR.status == 401) {
            await Swal.fire({
                icon: 'error',
                title: 'Su sessión expiró...',
                html: 'Ahora será redireccionado al Login...',
                timer: 4000,
                timerProgressBar: true,
                didOpen: () => {
                    Swal.showLoading();
                },
            }).then((result) => {
                // redireccionar al login
                location.replace(ret);
            });
        } else {
            await Swal.fire({
                    icon: 'error',
                    title: 'Se presentó el error siguiente:',
                    //text: jqXHR.responseJSON.detail ,
                    //timer: 5000, timerProgressBar: true,
                    didOpen: () => {
                        if (jqXHR == undefined || jqXHR.responseJSON == undefined) {
                            Swal.fire({
                                icon: 'error',
                                title: 'No se pudo establecer conexión con el servidor',
                                html: 'Ahora será redireccionado al Login...',
                                timer: 5000,
                                timerProgressBar: true,
                                didOpen: () => {
                                    Swal.showLoading();
                                },
                            }).then((result) => {
                                // redireccionar al login
                                location.replace(ret);
                            });
                        } else {
                            if (jqXHR.status == 422) {
                                // obtener el campo
                                campo = jqXHR.responseJSON.detail[0].loc[1]
                                if (campo != undefined) {
                                    mensaje = jqXHR.responseJSON.detail[0].msg
                                    if (mensaje == "value is not a valid integer" || mensaje == "value is not a valid float") {
                                        Swal.showValidationMessage(`El campo ${campo} debe ser un valor númerico`);
                                    } else if (mensaje == "field required") {
                                        Swal.showValidationMessage(`El campo ${campo} es requerido`);
                                    } else {
                                        Swal.showValidationMessage(mensaje);
                                    }

                                }
                            } else {
                                Swal.showValidationMessage(`${jqXHR.responseJSON.detail}`);
                            }
                        }
                    }
                })
                .then((result) => {
                    return true;
                });
        }
    }

    async function openNewTab(response, referencia, url, ret, tableToUpdate, closeModal, callback) {
        jqXHR = response[0];
        console.log('jqXHDR', 'jqXHR.responseJSON');
        console.log('jqXHDR', jqXHR);
        if (jqXHR.status == 200) {
            console.log('jqXHDR', jqXHR.responseJSON.message);
            if (jqXHR.responseJSON.message == "ok") {
                $(closeModal).modal("toggle");
                updatetbl(tableToUpdate); // actualizar la tabla
                var win = window.open(jqXHR.responseJSON.url, '_blank');
                if (win) {
                    win.focus(); //Browser has allowed it to be opened
                } else {
                    showMessagePopupbloqueados();
                }
            } else {
                Swal.fire({
                    icon: 'warning',
                    title: 'Mensaje recibido:',
                    didOpen: () => {
                        Swal.showValidationMessage(`${jqXHR.responseJSON.message}\n${jqXHR.responseJSON.reftramite}`);
                    }
                }).then((result1) => {
                    Swal.fire({
                        title: "Capture el número inicial para el trámite\n" +
                            jqXHR.responseJSON.reftramite,
                        html: 'Capture el numero 65 si el ultimo trámite es 64,' +
                            '<br> pero si será el primero del nuevo año capture 1' +
                            '<br>Nota. Este mensaje solo será mostrado cuando ' +
                            '<br>no se tenga un #consecutivo para los datos especificados.',
                        //icon: 'question',
                        input: 'number',
                        inputPlaceholder: 'Número del trámite siguiente?',
                        inputAttributes: { min: 1 },
                        showCancelButton: true,
                        cancelButtonText: "Cancelar",
                        confirmButtonText: "Sí, confirmar",
                        inputValidator: numexec => {
                            if (!numexec) {
                                return "Capture un valor numérico superior a 0";
                            } else {
                                try {
                                    numint = parseInt(numexec)
                                    if (numint <= 0) {
                                        return "Capture un valor numérico superior a 0";
                                    }
                                    return undefined;
                                } catch (error) {
                                    return "Capture un valor numérico por favor";
                                }
                            }
                        }
                    }).then((numexec) => {
                        callback(numexec.value);
                    });
                });
            }
        } else {
            // if error en jqXHR
            showMsg(jqXHR, referencia, url, ret).then(() => {});
        }
    }

    function fillSelect(objSelectDado, opciones) {
        // Rellena un objeto Html de tipo Select, con las opciones dadas
        $("#" + objSelectDado).empty();
        $.each(opciones, function(key, value) {
            $("#" + objSelectDado).append(
                '<option value="' + key + '">' + value + '</option>'
            );
        });
    }

    async function setDatosEnForm(objDado, formDado, prefIdObjHtml, postIdObjHtml, configAct) {
        return new Promise((resolve) => {
            // console.log(objDado);
            if (objDado) {
                //si el objeto está vacío no se ejecuta el each y no asigna valores al formulario
                $.each(objDado, function(key, value) {
                    // console.log( key + ": " + value );
                    idObJHtml = `#${formDado} #${prefIdObjHtml}${key}${postIdObjHtml}`;
                    objHtmlForm = $(idObJHtml)[0];
                    //console.log(objHtmlForm.nodeName);
                    if (objHtmlForm == undefined) {
                        alert("Developer: Hizo falta un objeto Html en el form: " + `${formDado} con id: ${prefIdObjHtml}${key}${postIdObjHtml}`);
                    } else if (["INPUT", "TEXTAREA"].includes(objHtmlForm.nodeName)) {
                        // console.log($(idObJHtml));
                        if ($(idObJHtml)[0].type == "checkbox") {
                            // console.log("value: " + value);
                            if (value) {
                                // $(idObJHtml).val(1);
                                $(idObJHtml).attr('checked', true);
                            } else {
                                // $(idObJHtml).val(0);
                                $(idObJHtml).attr('checked', false);
                            }
                        } else {
                            $(idObJHtml).val(value);
                        }
                    } else if (objHtmlForm.nodeName == "SELECT") {
                        if (value) {
                            $(idObJHtml).val(value);
                        } else {
                            $(idObJHtml).val("").trigger('change');
                        }
                    }
                });
            }
            // console.log(configAct.fuce);
            // habilitar para escritura los campos recibidos del servidor y se tenga permiso para editar
            if (configAct) {
                $.each(configAct.fuce, function(key, value) {
                    idObJHtml = `#${formDado} #${prefIdObjHtml}${value}${postIdObjHtml}`;
                    // console.log('idObjHtml', idObJHtml);
                    // console.log($(idObJHtml)[0].id);
                    // console.log($(idObJHtml)[0].type);
                    if (configAct.isEditable) {
                        // console.log('Aplicando a modo escritura a :' + idObJHtml);
                        // console.log($(idObJHtml)[0].type);
                        if ($(idObJHtml)[0].type == "checkbox") {
                            $(idObJHtml).removeAttr("disabled");
                        } else {
                            $(idObJHtml).removeAttr("readonly");
                        }
                        if ($(idObJHtml)[0].type == "select-one") {
                            // console.log("SELECT encontrado..");
                            if (!objDado.id) {
                                console.log("objeto vacio...");
                                // console.log($(idObJHtml)[0]);
                                // $(idObJHtml).val('-1').trigger('change');
                                // $(idObJHtml+" > option[value='-1']").attr("selected", true)
                            }
                        }
                    } else {
                        // si los campos no son editables y no estan definidos como readonly o disabled en rowinput
                        // desabilitarlos aquí.
                        if ($(idObJHtml)[0].type == "checkbox") { $(idObJHtml).attr("disabled"); }
                        if ($(idObJHtml)[0].type == "select-one") { disabledSelect2('#' + $(idObJHtml)[0].id); }
                    }
                });
            }
            resolve(true);
        });
    }

    async function setSelect(idObjSelect, idObjSelectOption, urlObjSelect, urlTypeAjax, paramsSelectUser, allowClear, setDisabled, urlFiltros, msgSinRegistros, minimoBusqueda, multipleactivo, ListOmitir) {
        return new Promise((resolve) => {
            text = "Selecciona una opción";
            minimumResult = "Infinity";

            if (minimoBusqueda != null) {
                text = "Busca una opción";
                minimoBusqueda = minimoBusqueda;
                minimumResult = 0;
            }
            if (idObjSelectOption == null) {
                idObjSelectOption = "";
                $(idObjSelectOption).empty();
            }
            multipleval = false;
            if (multipleactivo != null) {
                multipleval = multipleactivo
            }
            // objeto Html Select manipulado con la librería select2
            var objSelect = $(idObjSelect).select2({
                minimumInputLength: minimoBusqueda,
                multiple: multipleval,
                language: "es",
                minimumResultsForSearch: minimumResult,
                theme: "bootstrap",
                language: {
                    "noResults": function() {
                        if (msgSinRegistros) {
                            //return "No Results Found <a href='#' class='btn btn-danger'>Use it anyway</a>";
                            return msgSinRegistros;
                        } else {
                            return "Sin registros...";
                        }
                    }
                },
                escapeMarkup: function(markup) {
                    return markup;
                },
                with: '100%',
                dropdownParent: $(idObjSelect).parent(),
                allowClear: allowClear,
                placeholder: { id: '-1', text: text },
                ajax: {
                    delay: 250, // wait 250 milliseconds before triggering the request
                    type: urlTypeAjax,
                    url: urlObjSelect,
                    contentType: 'application/json',
                    data: function(params) {
                        var query = {
                                q: params.term,
                                //q_user_id: '{{user.id}}', // agregar paráms adicionales
                            }
                            // append urlFiltros
                            // Query parameters will be ?search=[term]&type=public
                        return query;
                    },
                    processResults: function(res) {
                        let jsonObj = [];
                        jsonObj.push({ 'id': '-1', text })
                        res.data.forEach((data) => {
                            let item = {};
                            item['id'] = data[0];
                            item['text'] = data[1];
                            if (data[2] && data[2] != null) {
                                item['disabled'] = true
                            }
                            //realizar validación
                            $.each(ListOmitir, function(index, id) {

                                if (id == data[0]) {
                                    item['disabled'] = true;
                                }
                            });
                            jsonObj.push(item);
                        });
                        return { results: jsonObj };
                    }
                }
            });
            // console.log("valor combo: "+idObjSelectOption)
            // Set the value, creating a new option if necessary
            if ($(idObjSelect).find("option[value='" + idObjSelectOption + "']").length) {
                $(idObjSelect).val(idObjSelectOption).trigger('change');
            } else if (idObjSelectOption == "") {
                $(idObjSelect).val('').trigger('change');
            } else {
                simbolo = "?";
                if (urlObjSelect.indexOf("?") >= 0) {
                    simbolo = "&";
                }
                $.ajax({
                    type: urlTypeAjax,
                    url: urlObjSelect + simbolo + paramsSelectUser,
                    //contentType:'application/json',
                    //data: stringifyData,
                }).then(function(res) {
                    let jsonObj = [];
                    res.data.forEach(data => {
                        let item = {};
                        item['id'] = data[0];
                        item['text'] = data[1];
                        jsonObj.push(item);
                        var option = new Option(data[1], data[0], true, true);
                        objSelect.append(option);
                    });
                    objSelect.trigger('change');
                });
            }
            if (setDisabled == true) {
                $(idObjSelect).select2({ "readonly": true });
                var selectId = idObjSelect.slice(1);
                // Aplicar el select como solo lectura
                var $select = $('#' + selectId).select2();
                $select.each(function(i, item) {
                    $(item).select2("destroy");
                });
                $("#" + selectId).attr("readonly", true);
            }
            setTimeout(() => {
                resolve(true);
            }, 350);
        });
    }

    function getMesesDelAnio() {
        return ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
    }

    function getFechasIniFinMes(Anio, habilitarAPartirDelMes, getIniOrFin) {
        // Preparar el select con datos de un Arreglo
        let dataSelect = [];
        if (Anio) {
            $.each(getMesesDelAnio(), function(index, valor) {
                index += 1;
                let item = {};
                printIndex = index <= 9 ? "0" + index : index;
                if (getIniOrFin.toUpperCase().startsWith("I")) {
                    item['id'] = "" + Anio + "-" + printIndex + "-01";
                    item['text'] = "01/" + printIndex + "/" + Anio;
                } else {
                    var dateLastDay = new Date(Anio, index, 0);
                    lastDay = moment(dateLastDay).daysInMonth();
                    item['id'] = "" + Anio + "-" + printIndex + "-" + lastDay;
                    item['text'] = lastDay + "/" + printIndex + "/" + Anio;
                }
                letItBeSelected = "";
                if (index <= habilitarAPartirDelMes) {
                    letItBeSelected = "1";
                }
                item['habilitado'] = letItBeSelected;
                dataSelect.push(item);
            });
            return dataSelect;
        }
        return dataSelect;
    }

    function getFechaAct() {
        return moment().format('YYYY-MM-DD');
    }

    function getFechasFinMes(Anio) {
        return moment().format('M');
    }

    function getMesActualNum() {
        return moment().format('MM');
    }

    function getNombreMes(numes) {
        moment.locale('es');
        return moment().month(numes - 1).format("MMMM");
    }

    function getCapitulos() {
        return ['1000', '2000', '3000', '4000', '5000', '6000', '7000', '8000', '9000'];
    }

    function gettotalescomision() {
        return ['Viáticos', 'Pasajes', 'Combustible', 'Otros Gastos'];
    }

    function gettiporecorrido() {
        return ['Traslado', 'Retorno', 'Recorrido interno'];
    }

    function gettiporecorridoitinerario() {
        return ['Traslado', 'Recorrido interno', 'Retorno'];
    }

    function gettipopartida() {
        return ['Emisora', 'Receptora'];
    }

    function getPptoStatusAutorizado() {
        return [{ id: 2, text: "Autorizado" }];
    }

    function getFiltroPresupuesto() {
        return ['Actividades', 'Partidas'];
    }

    async function setSelectArray(idInputSelect, modalParent, msgPlaceholder, dataArray, valorInicial) {
        return new Promise((resolve) => {
            // Preparar el select con datos de un Arreglo
            let dataSelect = [];
            $.each(dataArray, function(index, valor) {
                tipoValor = String(typeof(valor));
                let item = {};
                if (tipoValor == "object") {
                    item['id'] = valor.id;
                    item['text'] = valor.text;
                    if (valor.habilitado && valor.habilitado != null && valor.habilitado.length != 0) {
                        item['disabled'] = valor.habilitado
                    }
                } else {
                    index += 1;
                    item['id'] = index;
                    item['text'] = valor;
                }
                dataSelect.push(item);
            });
            $(idInputSelect).select2({
                theme: "bootstrap",
                dropdownParent: $(modalParent),
                minimumInputLength: 0,
                minimumResultsForSearch: "Infinity",
                data: dataSelect,
                placeholder: { id: '-1', text: msgPlaceholder },
                allowClear: true
            });
            if (valorInicial) {
                $(idInputSelect).val(valorInicial).trigger('change');
            }

            resolve(true);
        });
    }

    async function setSelectWith(idComboSelect, opciones, valSeleccionado) {
        return new Promise((resolve) => {
            // opciones = [ ["si", "si"], ["no", "no"] ];
            $(idComboSelect).empty();
            $.each(opciones, function(key, value) {
                var optselected = "";
                if (valSeleccionado != undefined) {
                    optselected = ("" + valSeleccionado) == ("" + value[0]) ? " selected" : "";
                }
                $(idComboSelect).append('<option value="' + value[0] + '"' + optselected + ' >' + value[1] + '</option>');
            });
            resolve(true);
        });
    }


    // --------------------------------
    function setStylePagination(idtblPaginator) {
        let data = $(idtblPaginator + " ul.pagination").children();
        for (let i = 0; i < data.length; i++) {
            data[i].classList.add("page-item");
            data[i].firstElementChild.classList.add("page-link");
        }
    }

    function setPageOneOnPaginator(idtblPaginador) {
        $(idtblPaginador + " ul.bootpag").find("li.active").removeClass("active");
        $(idtblPaginador + " ul.bootpag").find("li").first().next().addClass("active");
    }

    function queryParams(idTblToolSearch, idtblLimit, idtblPaginator) {
        var params = {};
        $(idTblToolSearch)
            .find("input[name]")
            .each(function() {
                params[$(this).attr("name")] = $(this).val();
            });
        $(idTblToolSearch)
            .find("select[name]")
            .each(function() {
                params[$(this).attr("name")] = $(this).val();
            });
        params["limit"] = $(idtblLimit).val();
        //console.log($(idtblLimit).val());
        let pagination_data = $(idtblPaginator + " ul.bootpag").find("li.active").children().text();
        params["pagination_position"] = pagination_data;
        params["offset"] = "0";
        return params;
    }

    // --------------------------------
    function dateFormatFH(date) {
        moment.locale('es');
        if (date != null) {
            fechaDada = moment(date);
            hoy = moment(Date.now());
            diffDias = hoy.diff(fechaDada, 'days');
            diffAnios = hoy.diff(fechaDada, 'years');
            if (diffDias == 0) {
                return moment(date).format('h:mm a')
            } else if (diffAnios == 0) {
                return moment(date).format('DD MMM h:mm a')
            } else {
                return moment(date).format('DD MMM, YYYY h:mm a')
            }
        } else {
            return ''
        }
    }

    function dateFormatF(date) {
        moment.locale('es');
        if (date != null) {
            return moment(date).format('DD MMM, YYYY')
        } else {
            return ''
        }
    }

    function dateFormatH(date) {
        moment.locale('es');
        if (date != null) {
            return moment(date).format('h:mm a')
        } else {
            return ''
        }
    }

    function setLimitsEnFechaField(idHtmlFecha, valFechaMin, valFechaMax) {
        if (valFechaMin) {
            $(idHtmlFecha).attr("min", valFechaMin);
        }
        if (valFechaMax) {
            $(idHtmlFecha).attr("max", valFechaMax);
        }
    }

    ///formato de moneda
    function monetaryFormat(number) {
        if (number != null) {
            var myNumeral = numeral(number);
            return currencyString = myNumeral.format('$0,0.00')
        } else {
            return ''
        }
    }

    function formatoMiles(num) {
        if (num != null) {
            return miles = numeral(num).format('0,0[.]00')
        } else {
            return ''
        }
    }
    //FORMATO SEPARADOR DE MILES EN MONEDA
    function milesFormat(v) {
        v = v.replace(/[\.][\.]/g, '').replace(/^[\.]/, '').replace(/([^0-9\.]+)/g, '');
        v = v.replace(/\.(\d{1,2})\./g, '.$1').replace(/\.(\d)(\d)(\d)/g, '.$1$2');
        v = v.toString().split('').reverse().join('').replace(/(\d{3})/g, '$1,');
        v = v.split('').reverse().join('').replace(/^[\,]/, '');
        return v;
    }
    //FORMATO SEPARADOR DE MILES CON UNA CLASE
    $('.milesFormat').on('keyup', function(event) {
        $(this).val(function(index, value) {
            return milesFormat(value);
        });
    });

    //version 2, no se mantiene el punto decinal ;(
    $('.formatoMiles').on('input', function(event) {
        $(this).val($(this).val().replace(/[^0-9,.-]/g, '').replace(/./g, '.0'));
        $(this).val(function(index, value) {
            console.log('value: ', value);
            return formatoMiles(value);
        });
        // $(this).val(formatoMiles(numeral($(this).val()).value()));
    });

    //v2 de separadormilesFormat(idForm). separar en miles los inputs con la clase "separadordeMiles" en un formulario, la clase debe estar en inputClass
    function separadorMilesForm(idForm) {
        $('#' + idForm + ' .separadordeMiles').each(function() {
            $(this).val(formatoMiles($(this).val()));
        });
    }

    // v2 de parsearforms_milesFormat(idForm). Parsear a valor numérico los inputs con separador de miles. la clase debe estar en inputClass
    function parsearforms_formatoMiles(idForm) {
        $('#' + idForm + ' .separadordeMiles').each(function() {
            // console.log('parsing: ',numeral($(this).val()).value() );
            $(this).val(numeral($(this).val()).value());
        });
    }
    // Quitar espacios de extremos para que el e.preventDefault(); válide correctamente
    function removespacesExtrems(idForm) {
        $('#' + idForm + ' textarea , input[type=text]').each(function() {
            $(this).val($.trim($(this).val()));
        });
    }


    // PARSEANDO INPUTS PASANDO EL ID DEL FORMULARIO
    // function parsearforms_milesFormat(idForm) {
    //     $('#' + idForm + ' .separadordeMiles input').each(function() {
    //         $(this).val(parseFloat($(this).val().replace(/[\,]/g, '')));
    //     });
    // }
    //ASIGNANDO SEPARADOR DE MILES A UN FORMULARIO CON EL DEL ID FORM
    // function separadormilesFormat(idForm) {
    //     $('#' + idForm + ' .separadordeMiles input').each(function() {
    //         $(this).val(milesFormat($(this).val()));
    //     });
    // }


    // --------------------------------

    // Para limpiar el history del navegador y evitar la opción de backhistory
    // https://newbedev.com/how-to-clear-browsing-history-using-javascript
    // se usó location.replace en los href de Salir/Logout en el html

    // una opción mas par garantizar la eliminación del history:
    //  https://www.cluemediator.com/how-to-disable-the-browser-back-button-using-javascript
    function disableBack() { window.history.forward(); }
    //setTimeout("disableBack()", 0);
    window.onunload = function() { null };

    /*
      // OPCION 1. http://jsbin.com/yaqaho/edit?html,css,js,output
      (function (global) {
        if(typeof (global) === "undefined") {
          throw new Error("window is undefined");
        }
        var _hash = "!";
        var noBackPlease = function () {
            global.location.href += "#";
        // making sure we have the fruit available for juice....
        // 50 milliseconds for just once do not cost much (^__^)
            global.setTimeout(function () {
                global.location.href += "!";
            }, 50);
        };
        // Earlier we had setInterval here....
        global.onhashchange = function () {
            if (global.location.hash !== _hash) {
                global.location.hash = _hash;
            }
        };
        global.onload = function () {
        noBackPlease();
        // disables backspace on page except on input fields and textarea..
        document.body.onkeydown = function (e) {
                var elm = e.target.nodeName.toLowerCase();
                if (e.which === 8 && (elm !== 'input' && elm  !== 'textarea')) {
                    e.preventDefault();
                }
                // stopping event bubbling up the DOM tree..
                e.stopPropagation();
            };
        };
      })(window);
      */
    /*
    const onHashChange = useCallback(() => {
    const confirm = window.confirm(
        'Warning - going back will cause you to loose unsaved data. Really go back?',
    );
    window.removeEventListener('hashchange', onHashChange);
    if (confirm) {
        setTimeout(() => {
        window.history.go(-1);
        }, 1);
    } else {
        window.location.hash = 'no-back';
        setTimeout(() => {
        window.addEventListener('hashchange', onHashChange);
        }, 1);
    }
    }, []);

    useEffect(() => {
    window.location.hash = 'no-back';
    setTimeout(() => {
        window.addEventListener('hashchange', onHashChange);
    }, 1);
    return () => {
        window.removeEventListener('hashchange', onHashChange);
    };
    }, []);      
    */
    async function getDataFromServer(Swal, datos, url, typeSubmit, ret, serializedData) {
        await $.ajax({
                type: typeSubmit,
                url: url,
                contentType: 'application/json',
                data: serializedData,
                success: function(data, textStatus, jqXHR) {
                    datos[0] = jqXHR;
                    Swal.close();
                },
                error: function(jqXHR, textStatus, error) {
                    // Cerrar Swal de procesando...
                    // console.log(jqXHR); console.log(textStatus); console.log(error);
                    datos[0] = jqXHR;
                    Swal.close();
                    //showMsg(jqXHR, referencia, url, ret);
                }
            }) // ajax
    }

    async function sendDatosToServer(referencia, url, typeSubmit, ret, serializedData) {
        let datos = [""];
        await Swal.fire({
            title: 'Procesando...',
            toast: true,
            showConfirmButton: false,
            showCancelButton: false,
            allowEscapeKey: false,
            didOpen: (resp) => {
                    Swal.showLoading();
                    getDataFromServer(Swal, datos, url, typeSubmit, ret, serializedData);
                } //didOpen
        });

        return datos;
    }

    async function showProcessingMsg(titulo, mensaje) {
        // Función para representar visualmente algun procesamiento empleando un componente Swal
        await Swal.fire({
            title: titulo,
            // toast: false,
            showConfirmButton: false,
            showCancelButton: false,
            allowEscapeKey: false,
            allowOutsideClick: false,
            // closeOnClickOutside: false,
            backdrop: true,
            didOpen: (resp) => {
                Swal.showLoading();
                Swal.showValidationMessage(mensaje);
            }
        });
    }

    //validar inputs, selects, textarea de todos los formularios con la clase 'needs-validation'

    (function() {
        'use strict';
        window.addEventListener('load', function() {
            // Fetch all the forms we want to apply custom Bootstrap validation styles to
            var forms = document.getElementsByClassName('needs-validation');
            // Loop over them and prevent submission
            var validation = Array.prototype.filter.call(forms, function(form) {
                form.addEventListener('submit', function(event) {
                    if (form.checkValidity() === false) {
                        event.preventDefault();
                        event.stopPropagation();
                    }
                    form.classList.add('was-validated');
                }, false);
            });
        }, false);
    })();

    function showMsgTemporal(tiempo, icono, titulo, mensaje) {
        Swal.fire({
            icon: icono,
            title: titulo,
            text: mensaje,
            timer: tiempo
        })
    }

    async function downloadPlantilla(cat, typeAjax, url, referencia, ret) {
        $.ajax({
            type: typeAjax,
            url: url,
            xhr: function() {
                var xhr = new XMLHttpRequest();
                xhr.onreadystatechange = function() {
                    if (xhr.readyState == 2) {
                        // si hubo una repuesta SUCCESS del servidor entonces 
                        // preparar la recepción del archivo (tipo blob)
                        // y si no entonces recibir la responseJSON
                        if (xhr.status == 200) {
                            xhr.responseType = "blob";
                        } else {
                            xhr.responseType = "text";
                        }
                    }
                };
                return xhr;
            },
            success: function(blob) {
                // console.log(blob.size);
                var link = document.createElement('a');
                link.href = window.URL.createObjectURL(blob);
                //link.download = cat + new Date() + ".xlsx";
                link.download = cat + ".xlsx";
                link.click();
            },
            error: function(jqXHR, textStatus, error) {
                // console.log(error); console.log(textStatus); console.log(jqXHR);
                showMsg(jqXHR, referencia, url, ret);
            }
        });
    }

    function setUploadFiles(typeAjax, selectorInput, urlDada, formsubir, estructTiposArch, callback) {
        // First register any plugins
        $.fn.filepond.registerPlugin(FilePondPluginFileValidateType //, FilePondPluginImagePreview
        );
        inputElement = document.querySelector(selectorInput);
        arrTipArch = []
        $.each(estructTiposArch, function(tipoArch, extension) {
            arrTipArch.push(tipoArch);
        });
        pond = FilePond.create(inputElement, {
            allowMultiple: false,
            instantUpload: false,
            allowProcess: false,
            acceptedFileTypes: arrTipArch,
            fileValidateTypeLabelExpectedTypesMap: estructTiposArch,
            instantUpload: true
                // , maxFileSize: '1MB' // Esta propiedad no funciona...
                ,
            allowRevert: true,
            fileValidateTypeLabelExpectedTypes: 'Se esperaba: {allButLastType} or {lastType}',
            labelIdle: "<span class='filepond--label-action'>Busca</span> o arrastra y suelta aquí tu archivo",
            labelFileTypeNotAllowed: "Archivo de tipo inválido",
            server: {
                url: "",
                revert: null,
                process: {
                    url: urlDada,
                    method: typeAjax,
                    ondata: (formData) => {
                        var fd = new FormData();
                        // solo incorporar inputs "files" de tipo object y otros adicionales en el form
                        for (var pair of formData.entries()) {
                            key = pair[0];
                            value = pair[1];
                            if (!(key == "files" && String(typeof value) == "string")) {
                                fd.append(key, value);
                            }
                        }
                        // Anexar el tipo de importación (tdi) seleccionado en el form
                        formData = fd;
                        formData.append('tdi', $("#" + formsubir + " #tdi").val());

                        return formData;
                    },
                    onload: (res) => {
                        callback(res, "onload");
                    },
                    onerror: (res) => {
                        callback(res, "onerror");
                    }
                }
            }
        });
        //pond.addFile('../../ER.png');

        // Manually add a file using the addfile method
        // $('.input-file').first().filepond('addFile', 'index.html').then(function(file){
        //     console.log('file added', file);
        // });
        return pond;
    }

    function setUploadFilesData(typeAjax, selectorInput, urlDada, formsubir, estructTiposArch, callback) {
        // First register any plugins
        $.fn.filepond.registerPlugin(FilePondPluginFileValidateType, FilePondPluginGetFile);
        inputElement = document.querySelector(selectorInput);
        arrTipArch = [];
        $.each(estructTiposArch, function(tipoArch, extension) {
            arrTipArch.push(tipoArch);
        });
        pond = FilePond.create(inputElement, {
            allowMultiple: false,
            instantUpload: false,
            allowProcess: false,
            acceptedFileTypes: arrTipArch,
            fileValidateTypeLabelExpectedTypesMap: estructTiposArch,
            instantUpload: true,
            allowRevert: true,
            fileValidateTypeLabelExpectedTypes: 'Se esperaba: {allButLastType} or {lastType}',
            labelIdle: "<span class='filepond--label-action'>Busca</span> o arrastra y suelta aquí tu archivo",
            labelFileTypeNotAllowed: "Archivo de tipo inválido",
            server: {
                url: "",
                process: {
                    url: urlDada,
                    method: typeAjax,
                    ondata: (formData) => {
                        var fd = new FormData();
                        // solo incorporar inputs "files" de tipo object y otros adicionales en el form
                        for (var pair of formData.entries()) {
                            key = pair[0];
                            value = pair[1];
                            if (!(key == "files" && String(typeof value) == "string")) {
                                fd.append(key, value);
                            }
                        }
                        // Anexar el tipo de importación (tdi) seleccionado en el form
                        formData = fd;
                        let serializedData = JSON.stringify($('#' + formsubir).serializeJSON());
                        formData.append('datos', serializedData);
                        // console.log(serializedData);
                        return formData;
                    },
                    onload: (res) => {
                        callback(res, "onload");
                    },
                    onerror: (res) => {
                        callback(res, "onerror");
                    }
                }
            }
        });
        $('#' + formsubir + ' ' + selectorInput).on('FilePond:processfilestart', function(e) {
            showProcessingMsg("Procesando...", "Esta operación puede tardar algunos minutos...")
                // console.log('file add event', e.detail);
                // $("#" + msgError).addClass('d-none');
        });
        $('#' + formsubir + ' ' + selectorInput).on('FilePond:error', function(e) {
            try {
                Swal.close();
            } catch (error) {
                console.log(error);
            }
            // console.log('file error event', e.detail);
            // $("#" + msgError).addClass('d-none');
        });
        return pond;
    }

    function cleanMsgUploadFile(formsubir, msgError, pond) {
        $("#" + formsubir).trigger('reset');
        $("#" + msgError).addClass('d-none');
        pond.removeFile();
    }

    //Funcion creada por el detallle que en la funcion original recibe un select
    function setUploadFotos(typeAjax1, selectorInput1, urlDada1, formsubir1, msgError1, estructTiposArch1, callback) {
        // First register any plugins
        $.fn.filepond.registerPlugin(FilePondPluginFileValidateType //, FilePondPluginImagePreview
        );
        inputElement = document.querySelector(selectorInput1);
        arrTipArch = []
        $.each(estructTiposArch1, function(tipoArch, extension) {
            arrTipArch.push(tipoArch);
        });
        pond1 = FilePond.create(inputElement, {
            allowMultiple: false,
            instantUpload: false,
            allowProcess: false,
            acceptedFileTypes: arrTipArch,
            fileValidateTypeLabelExpectedTypesMap: estructTiposArch1,
            instantUpload: true,
            maxFileSize: '5MB',
            allowRevert: true,
            fileValidateTypeLabelExpectedTypes: 'Se esperaba: {allButLastType} or {lastType}',
            labelIdle: "<span class='filepond--label-action'>Busca</span> o arrastra y suelta aquí tu archivo",
            labelFileTypeNotAllowed: "Archivo de tipo inválido",
            server: {
                url: "",
                revert: null,
                process: {
                    url: urlDada1,
                    method: typeAjax1,
                    ondata: (formData) => {
                        var fd = new FormData();
                        // solo incorporar inputs "files" de tipo object y otros adicionales en el form
                        for (var pair of formData.entries()) {
                            key = pair[0];
                            value = pair[1];
                            if (!(key == "files" && String(typeof value) == "string")) {
                                fd.append(key, value);
                            }
                        }
                        // Anexar el tipo de importación (tdi) seleccionado en el form
                        formData = fd;
                        //formData.append('tdi', $("#" + formsubir + " #tdi").val());
                        return formData;
                    },
                    onload: (res) => {
                        callback(res, "onload");
                    },
                    onerror: (res) => {
                        callback(res, "onerror");
                    }
                }
            }
        });

        // Manually add a file using the addfile method
        // $('.input-file').first().filepond('addFile', 'index.html').then(function(file){
        //     console.log('file added', file);
        // });
        return pond1;
    }

    function cleanMsgUploadFile(formsubir1, msgError1, pond1) {
        $("#" + formsubir1).trigger('reset');
        $("#" + msgError1).addClass('d-none');
        pond1.removeFile();
    }

    //Funcion creada por problemas de ID, ya que indexbase afectaba a los demas modulos  
    function setUploadFotoPer(typeAjax2, selectorInput2, urlDada2, formsubir2, msgError2, estructTiposArch2, callback) {
        // First register any plugins
        $.fn.filepond.registerPlugin(FilePondPluginFileValidateType //, FilePondPluginImagePreview
        );
        inputElement = document.querySelector(selectorInput2);
        arrTipArch = []
        $.each(estructTiposArch2, function(tipoArch, extension) {
            arrTipArch.push(tipoArch);
        });
        pond2 = FilePond.create(inputElement, {
            allowMultiple: false,
            instantUpload: false,
            allowProcess: false,
            acceptedFileTypes: arrTipArch,
            fileValidateTypeLabelExpectedTypesMap: estructTiposArch2,
            instantUpload: true,
            maxFileSize: '5MB',
            allowRevert: true,
            fileValidateTypeLabelExpectedTypes: 'Se esperaba: {allButLastType} or {lastType}',
            labelIdle: "<span class='filepond--label-action'>Busca</span> o arrastra y suelta aquí tu archivo",
            labelFileTypeNotAllowed: "Archivo de tipo inválido",
            server: {
                url: "",
                revert: null,
                process: {
                    url: urlDada2,
                    method: typeAjax2,
                    ondata: (formData) => {
                        var fd = new FormData();
                        // solo incorporar inputs "files" de tipo object y otros adicionales en el form
                        for (var pair of formData.entries()) {
                            key = pair[0];
                            value = pair[1];
                            if (!(key == "files" && String(typeof value) == "string")) {
                                fd.append(key, value);
                            }
                        }
                        // Anexar el tipo de importación (tdi) seleccionado en el form
                        formData = fd;
                        //formData.append('tdi', $("#" + formsubir + " #tdi").val());
                        return formData;
                    },
                    onload: (res) => {
                        callback(res, "onload");
                    },
                    onerror: (res) => {
                        callback(res, "onerror");
                    }
                }
            }
        });

        // Manually add a file using the addfile method
        // $('.input-file').first().filepond('addFile', 'index.html').then(function(file){
        //     console.log('file added', file);
        // });
        return pond2;
    }

    function cleanMsgUploadFile(formsubir2, msgError2, pond2) {
        $("#" + formsubir2).trigger('reset');
        $("#" + msgError2).addClass('d-none');
        pond2.removeFile();
    }
    //select2
    function select2Readonly(idSelect, select_user_id, select_full_name) {
        var $select = $('#' + idSelect).select2();
        $select.each(function(i, item) {
            $(item).select2("destroy");
        });
        document.getElementById(idSelect).removeAttribute("multiple"); //quitamos elatributo multiple
        document.getElementById(idSelect).options.length = 0; //elimina todos los options
        $("#" + idSelect).attr("readonly", true);
        $("#" + idSelect).append( //agregamos la opci+on
            '<option value="' + select_user_id + '">' + select_full_name + '</option>'
        );
    }

    function getLabelOfFile(nomarchivo) {
        let nuevonombre = "";
        if (nomarchivo) {
            let longnomarchivo = nomarchivo.length;
            if (longnomarchivo >= 25) {
                nuevonombre = nomarchivo.substr(0, 25) + '...';
            } else {
                nuevonombre = nomarchivo;
            }

        }

        return nuevonombre;
    }

    async function filePondDisabledEnabled(pond, id, habilitar) {
        var filePondHabilitado;
        return new Promise((resolve) => {
            if (habilitar == "deshabilitar") {
                pond.setOptions({ disabled: true });
                filePondHabilitado = document.querySelector("#" + id + " .filepond--drop-label");
                filePondHabilitado.classList.remove("filepondAbilitado");
            } else if (habilitar == "habilitar") {
                pond.setOptions({ disabled: false });
                filePondHabilitado = document.querySelector("#" + id + " .filepond--drop-label");
                filePondHabilitado.classList.add("filepondAbilitado");
            }
            resolve(true);
        });
    }


    // ------------------------------------------------------------------------
    // Funciones destinadas a cambios de Actividades y habilitación de funciones en Procesos
    // ------------------------------------------------------------------------
    function desactivarBtnTermSiHayCambios(inputsOnChangeActivado, formDado) {
        if (inputsOnChangeActivado[0] == false) {
            inputsOnChangeActivado[0] = true;
            // console.log('inputsOnChangeActivado: ', inputsOnChangeActivado[0]);
            $("#" + formDado + " input").change(function() {
                desactivarBtnTerminar("cambioSolicStatusact");
            });
            $("#" + formDado + " select").change(function() {
                console.log("Cambio detectado en: " + formDado);
                console.log($(this));
                desactivarBtnTerminar("cambioSolicStatusact");
            });
            $("#" + formDado + " textarea").change(function() {
                desactivarBtnTerminar("cambioSolicStatusact");
            });
        }
    }

    function desactivarBtnTerminar(idInputHtmlWithSatutsact) {
        marcadoParaTerminar = $("#" + idInputHtmlWithSatutsact).val();
        if (marcadoParaTerminar && marcadoParaTerminar == "t") {
            btnChangeStatusAct("desactivar", "btnOperAct", "");
            console.log('btnTerminar desactivado por cambio');
        }
    }

    function btnChangeStatusAct(activar, btnDado, nvoNombre) {
        classActivar = "btn-primary";
        classDesactivar = "btn-secondary";
        if (activar == "desactivar") {
            $("#" + btnDado).removeClass(classActivar).addClass('disabled ' + classDesactivar);
        } else {
            $("#" + btnDado).removeClass('disabled ' + classDesactivar).addClass(classActivar);
        }
        if (nvoNombre.length > 0) {
            $("#" + btnDado + " .valor").html(nvoNombre);
        }
    }

    function setDatosTramite(configAct, btnGuardar) {
        $("#reftramite").val(configAct.reftramite);
        $("#actactual").val(configAct.actactual);
        $("#statusact").val(configAct.statusact);
        $("#statusdocto").val(configAct.statusdocto);
        $("#showbtns").val(configAct.showbtns);
        $("#tipoProcact").val(configAct.tipoProcact);
        $("#regresar_pas_id_userdest_id").val(configAct.regresarAct);
        $("#procactexect_ant_id").val(configAct.procactexect_anterior_id);
        if (configAct.objPe) {
            $("#asunto").val(configAct.objPe.asunto);
        }
        iconGuardar = "<span class='ti ti-device-floppy me-1 mb-0 h2'></span>";
        iconTerminar = "<span class='ti ti-clipboard-check me-1 mb-0 h2'></span>";
        iconAtender = "<span class='ti ti-clipboard me-1 mb-0 h2'></span>";
        // Deshabilitar la función de guardar y operaciones
        btnChangeStatusAct("desactivar", btnGuardar, iconGuardar + "Guardar Datos")
        btnChangeStatusAct("desactivar", "btnOperAct", iconAtender + "Terminar act.")
        if (configAct.statusact == "1") {
            $("#statusacttext").val("Por atender");
            if (configAct.showbtns.includes("a")) {
                $("#cambioSolicStatusact").val("a");
                btnChangeStatusAct("activar", "btnOperAct", iconAtender + "Atender act.")
            }
        } else if (configAct.statusact == "2") {
            $("#statusacttext").val("En atención");
            if (configAct.showbtns.includes("t")) {
                $("#cambioSolicStatusact").val("t");
                btnChangeStatusAct("activar", "btnOperAct", "");
                console.log('btnTerminar activado por status 2');
            }
            btnChangeStatusAct("activar", btnGuardar, "");
        } else if (configAct.statusact == "3") {
            $("#cambioSolicStatusact").val("x");
            $("#statusacttext").val("Terminada");
        } else if (configAct.statusact == "4") {
            $("#cambioSolicStatusact").val("x");
            $("#statusacttext").val("Cancelada");
        }
    }

    $("#opcionActRegresar").change(function() {
        $("#q_pas_id_userdest_id").prop("disabled", "disabled");
    });
    $("#opcionActSiguiente").change(function() {
        $("#q_pas_id_userdest_id").removeAttr("disabled");
    });


    function terminarAct(nombPaginaActual, codigoHtmlARastrear, procexec_id, procactexec_id, ret, proceso, callback, msg, urlchange, idform, idmodal) {
        formDado = "formTerminarAct";
        if (idform != null) {
            formDado = idform;
        }
        $('#' + formDado).addClass("was-validated");
        if (!$('#' + formDado)[0].checkValidity()) {
            $('#' + formDado + ' .invalid-feedback').each(function() {
                if ($(this)[0].offsetParent) {
                    $(this).parent().find("select, input, textarea").first().focus();
                    return false; // exit each
                }
            });
            return;
        }
        let nomUrl;
        // Si todo está correcto... Enviar la información al servidor
        nomSplit = nombPaginaActual.split('_');
        if (nomSplit.length == 2) {
            nomUrl = (nomSplit[1].split('.'))[0];
            //console.log('salio esto',nomUrl);
        } else {
            nomUrl = nomSplit[1];
        }
        cat = nombPaginaActual;
        referencia = cat + "." + codigoHtmlARastrear;
        if (proceso != null) {
            url = `/api/${nomUrl}/${proceso}/changeact/` + procexec_id + "/" + procactexec_id + "?ret=" + ret;
        } else {
            url = urlchange;
        }
        typeSubmit = "POST";
        formSer = $("#" + formDado).serializeJSON();
        if (formSer.id == "") { formSer.id = null; } // enviar null en vez de "" y evitar así error de pydantic
        serializedData = JSON.stringify(formSer);
        sendDatosToServer(referencia, url, typeSubmit, ret, serializedData).then((response) => {
            jqXHR = response[0];
            if (jqXHR.status == 200) {
                // Personalización para cuando esté todo correcto
                callback(jqXHR);
                if (msg == null) {
                    msg = "Esta actividad ha sido registrada como TERMINADA...";
                }
                idmod = "modalTerminarAct";
                if (idmodal != null) {
                    idmod = idmodal;
                }

                $("#" + idmod).modal('toggle');
                showMsg(jqXHR, referencia, url, ret, msg).then(() => {
                    $('#' + formDado).removeClass("was-validated");
                    if (jqXHR.responseJSON.respSigu && jqXHR.responseJSON.respSigu == "redirect") {
                        location.replace(jqXHR.responseJSON.url);
                    } else {
                        location.reload();
                    }
                });
            } else {
                showMsg(jqXHR, referencia, url, ret).then(() => {});
            }
        });
    }

    function openArchivoDisenio(url){
        var win = window.open(url);
        win.focus();
    }
    
    function obvserHist(procexec_id, ret, nombreProc){ 
        $('#procexec_id').val(procexec_id)
        let dataCom = []
        // $("#modalTerminarAct").modal('hide');
        $("#modal-obvserHist").modal('show');
        $("#t_modal_obvserHist").html("Historial del Trámite de " + nombreProc);
        
        referencia = 'scripts.js_ObservHist';
        url = "/api/histramite/" + procexec_id;
        $.ajax({
            type: 'GET',
            url: url,
            contentType: 'application/json',
            success: function(data, textStatus, jqXHR) {
                for (i = 0; i < data.data.length; i++) {
                    dataCom.push(data.data[i])
                }
                // limpiar filas existentes   
                $('#modal-histramite-table-plantilla' + ' tr').each(function() {
                    if ($(this)[0].id.startsWith("tr_")) {
                        $(this)[0].remove()
                    }
                });
                rellenarActsEnModal("#modal-histramite-table-plantilla", "#modal-histramite-tr-plantilla-act", dataCom);

            },
            error: function(jqXHR, textStatus, error) {
                showMsg(jqXHR, referencia, url, ret).then(() => {});
            }
        })
    }


    function rellenarActsEnModal(TblATrab, filATrab, data) {
        data.forEach(function(obj) {
            obj[0] == null ? obj[0] = 0 : obj[0]
            obj[1] == null ? obj[1] = 0 : obj[1]

            var nvafil = $(filATrab).clone(); // clonar la fila plantilla y dejarla como nueva fila
            nvafil.attr('id', 'tr_' + obj[0]); // asignar el nuevo id
            //  Añadir al final de la tabla, la nueva fila
            $(TblATrab).find("tr:last").after(nvafil);
            nvafil.find('.porc').html(obj[1] + "%");
            nvafil.find('.statusdocto').html(obj[2]);
            nvafil.find('.act').html(obj[3]);
            nvafil.find('.particip').html(obj[4]);
            nvafil.find('.periodoatencion').html(dateFormatFH(obj[5]) + ' - ' + dateFormatFH(obj[6]));

            if (obj[5] != null && obj[6] != null) {
                fecha1 = moment(obj[6]).format('h:mm ')
                fecha2 = moment(obj[5]).format('h:mm ')
                fecha1 = moment(fecha1, 'HH:mm');
                fecha2 = moment(fecha2, 'HH:mm');
                testim = moment.duration(fecha1 - fecha2).humanize()
                fechaatendida = moment(obj[6]);
                diffDias = fechaatendida.diff(obj[5], 'days');
                diffDias == 0 ? nvafil.find('.atenciontim').html(testim) : nvafil.find('.atenciontim').html(diffDias + " días y " + testim)
            }

            switch (obj[7]) {
                case '1':
                    nvafil.find('.on-off').addClass('bg-yellow');
                    nvafil.find('.on-off').attr("title", "Asignado");
                    break;
                case '2':
                    nvafil.find('.on-off').addClass('bg-orange');
                    nvafil.find('.on-off').attr("title", "Atención");
                    break;
                case '3':
                    nvafil.find('.on-off').addClass('bg-green');
                    nvafil.find('.on-off').attr("title", "Terminada");
                    break;
                case '4':
                    nvafil.find('.on-off').addClass('bg-red');
                    nvafil.find('.on-off').attr("title", "Cancelada");
                    break;
                case '5':
                    nvafil.find('.on-off').addClass('bg-blue');
                    nvafil.find('.on-off').attr("title", "Reasignada");
                    break;
                default:
                    nvafil.find('.on-off').addClass('bg-grey');
            }
            nvafil.show(); // mostrar la fila
        });

    }



    function changeStatusAct(referencia, url, ret,actBack) {
        // Si el status 
        statusact = $("#statusact").val();
        showbtns = $("#showbtns").val();
        estadotram = $("#tipoProcact").val();
        if (estadotram == 1 || actBack=='False') {
            $("#opcionActRegresar").prop('disabled', 'disabled');
            $("#regresarActividad").addClass('opcionActRegresar');
        }
        if (statusact == "1") {
            // Enviar al servidor la petición para atender la actividad
            // En el servidor se debe validar que este pe y pax
            // se encuentre en estado 1 y retornará el cambio de estado a "2"
            // Posicionar en la primer caja de captura habilitada 
            //   referencia = "changeStatusAct.scriptsjs";
            //   url = "/api/procs/changeact/"+ procexec_id + "/" + procactexec_id + "?ret=" + ret;
            typeSubmit = "POST";
            formSer = $("#" + formDado).serializeJSON();
            if (formSer.id == "") { formSer.id = null; } // enviar null en vez de "" y evitar así error de pydantic
            formSer.cambioSolicStatusact = "a";
            serializedData = JSON.stringify(formSer);
            console.log(serializedData);
            sendDatosToServer(referencia, url, typeSubmit, ret, serializedData).then((response) => {
                jqXHR = response[0];
                if (jqXHR.status == 200) {
                    msg = "Esta actividad ha sido registrada En Atención...";
                    showMsg(jqXHR, referencia, url, ret, msg).then(() => {
                        location.replace(ret);
                    });
                } else {
                    showMsg(jqXHR, referencia, url, ret).then(() => {});
                }
            });

        } else if (statusact == "2") {
            if (showbtns.includes("t")) {
                // Si está en atención y el botón se encuentra en Terminar
                // Se debe mostrar el modal correspondiente
                // obtener los datos de secuencia de la act. siguiente
                if(referencia=='proc_pago_efectuar.html'){
                    $("#opcionActRegresar").prop('disabled',true);
                }
                $('#modalTerminarAct').modal({ backdrop: 'static', keyboard: false });
                $("#modalTerminarAct").modal("show");
            }
        } else if (statusact == "3" || statusact == "4") {
            //
        }
    }

    function disabledSelect2(idObjSelect) {

        $(idObjSelect).select2({ "readonly": true });
        var selectId = idObjSelect.slice(1);
        // Aplicar el select como solo lectura
        var $select = $('#' + selectId).select2();
        $select.each(function(i, item) {
            $(item).select2("destroy");
        });
        $("#" + selectId).attr("readonly", true);
    }

    function percentageFormat(valor) {
        if (valor != null) {
            // console.log(valor+' %');
            return valor + ' %';
        } else {
            return ''
        }
    }

    function yaSePuedeTerminarAct(configAct) {
        let marcado_Terminar = $("#cambioSolicStatusact").val();

        if (configAct.statusact == "2") {
            if (configAct.showbtns.includes("t")) {
                if (marcado_Terminar && marcado_Terminar == "t") {
                    btnChangeStatusAct("activar", "btnOperAct", "");
                    console.log('btnTerminar activado por status 2 y t');
                }
            }
        }
    }

    function reportePreview(url) {
        console.log(url)
        var win = window.open(url, '_blank');
        win.focus();
    }


    function exportHtmlTableToPDF(idTabla, nombreArchivo) {
        $('#' + idTabla).tableExport({
            fileName: nombreArchivo,
            type: 'pdf',
            jspdf: {
                orientation: 'l',
                format: 'a3',
                margins: { left: 10, right: 10, top: 20, bottom: 20 },
                autotable: {
                    styles: {
                        fillColor: 'inherit',
                        textColor: 'inherit'
                    },
                    tableWidth: 'auto'
                }
            }
        });
    }

    function getobservaciones( procexec_id){
        $('#observacion').empty();
        // console.log(procexec_id);
        referencia = 'scripts.js_getobservaciones';
        url = "/api/observaciones/" + procexec_id;
        // console.log(url);
        $.ajax({
            type: 'GET',
            url: url,
            contentType: 'application/json',
            success: function(data, textStatus, jqXHR) {
                console.log('data', data.data);
                var splitdata = JSON.parse(data.data);
                $.each(splitdata, function(fecha, valor){
                    console.log(valor);
                    var indices = Object.keys(valor);
                    $.each(indices, function(i, valori){
                        console.log(i, valori);
                        if(valor[valori[0]].observaciones == ""){
                            console.log('No se toma el registro sin observaciones');
                            $(valor[valori[0]]).empty();
                            console.log(valor);
                        }else{
                            $('#observacion').append(`
                                <div class="card card-sm" id="observaciones">
                                    <div class="card-status-start bg-blue"></div>
                                    <div class="card-body">
                                        <div class="card-header d-flex justify-content-between" id="contenido">
                                            <p class="card-title titulo">${valor[valori[0]].empleado}</p>
                                            <p class="card-title fecha">${fecha}     ${valor[valori[0]].hora}</p>
                                        </div>
                                        <p class="text-muted observ">${valor[valori[0]].observaciones}</p>
                                    <div class="card-footer text-end" style="border: none;">${valor[valori[0]].actividad}</div>
                                </div>
                                </div>
                            `);
                        }
                    }); 
                });
            },
            error: function(jqXHR, textStatus, error) {
                // console.log(error); console.log(textStatus); console.log(jqXHR);
                showMsg(jqXHR, referencia, url, ret).then(() => {});
            }
        });
    }