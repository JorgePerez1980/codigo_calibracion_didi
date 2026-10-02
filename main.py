from execute import WorkFlow

def main(request) -> str:
    
    """Función principal que procesa un archivo CSV de transcripciones de llamadas.

    Args:
        event (dict): Un diccionario que contiene información del evento que activó la función.
                      Debe contener una clave 'name' con el nombre del archivo CSV a procesar.
        context: Contexto de ejecución de la función en Cloud Functions. No se utiliza en este caso.

    Returns:
        None.
    """

    WorkFlow(request).run()
    return "finish process"


#Nombre del audio de prueba
main(
        {
            "txt_1": "t360287971334589529.csv",
            "txt_2": "t360287971335330567.csv",
            "txt_3": "t360287971319554981.csv",
            # "txt_4": "t360287971320489251.csv",
            # "txt_5": "t360287971320226099.csv",
            # "txt_6": "t360287971289034158.csv",
            # "txt_7": "t360287971293496166.csv",
            # "txt_8": "t360287971294217218.csv",
            # "txt_9": "t360287971293424063.csv",
            # "txt_10": "t360287971293210173.csv",
            #"txt_11": "t360287971290098496.csv",
            #"txt_12": "t360287971292926735.csv",
            #"txt_13": "t360287971293215182.csv",
            #"txt_14": "t360287971293328728.csv",
            #"txt_15": "t360287971289668468.csv",
            # "txt_16": "t360287971293377387.csv",
            # "txt_17": "t360287971292933069.csv",
            # "txt_18": "t360287971288583346.csv",
            # "txt_19": "t360287971295048113.csv",
            # "txt_20": "t360287971288813991.csv",
            # "txt_21": "t360287971293051019.csv",
            # "txt_22": "t360287971289451210.csv",
            # "txt_23": "t360287971289117109.csv",
            # "txt_24": "t360287971289112422.csv",
            # "txt_25": "t360287971292904587.csv",

        }
    )
