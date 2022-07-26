from IPython.core.display import display, Javascript, HTML
import string
import random
import pkg_resources
import urllib
import json


def display_quiz(ref, num=1_000_000, shuffle_questions=False, shuffle_answers=True, preserve_responses=False):
    '''
    Display an interactive quiz (currently multiple-choice or numeric answer)
    using a mix of Python and Javascript to support use in rendered notebooks
    (especially JupyterBook, but also Voila)

    Inputs:
    ref = string, reference to quiz JSON, may be:
          - file name
          - URL
          - Python list
          - ID of HTML element with JSON as inner HTML
          - ID of HTML element with base64-encoded JSON as inner HTML

    shuffle_questions = boolean, whether to shuffle order of questions (default False)

    shuffle_answers = boolean, whether to shuffle answers for multiple-choice questions (default True)
    
    preserve_responses = boolean, whether to output the user responses in a way that is preserved upon reload of the notebook (default False)

    John  M. Shea
    9/26/2021
    '''


    assert not (shuffle_questions and preserve_responses), \
        "This package does not support preserving responses if questions are shuffled."
    resource_package = __name__

    letters = string.ascii_letters
    div_id = ''.join(random.choice(letters) for i in range(12))
    #print(div_id)

    if preserve_responses:
        preserve_json = "true"
    else:
        preserve_json = "false"



    mydiv = f"""<div id="{div_id}" data-shufflequestions="{str(shuffle_questions)}"
               data-shuffleanswers="{str(shuffle_answers)}"
               data-preserveresponses="{preserve_json}"
               data-numquestions="{str(num)}"> """
    #print(mydiv)

    styles = "<style>"
    css = pkg_resources.resource_string(resource_package, "styles.css")
    styles += css.decode("utf-8")
    styles += "</style>"

    script = '<script type="text/Javascript">'


    if isinstance(ref, list):
        #print("List detected. Assuming JSON")
        script += f"var questions{div_id}="
        script += json.dumps(ref)
        static = True
        url = ""
    elif isinstance(ref, str):
        if ref[0] == '#':
            script+=f'''var element=document.getElementById("{ref[1:]}");
            var questions;
            try {{
               questions{div_id}=JSON.parse(window.atob(element.innerHTML));
            }} catch(err) {{
               console.log("Fell into catch");
               questions{div_id} = JSON.parse(element.innerHTML);
            }}
            console.log(questions{div_id});'''
            static = True;
            #print(script)
        elif not ref.lower().find("http"):
            script += f"var questions{div_id}="
            url = ref
            file = urllib.request.urlopen(url)
            for line in file:
                script += line.decode("utf-8")
            static = False
        else:
            #print("File detected")
            script += f"var questions{div_id}="
            with open(ref) as file:
                for line in file:
                    script += line
            static = True
            url = ""
    else:
        raise Exception("First argument must be list (JSON), URL, or file ref")

    script += ''';
    '''


    #display(HTML(mydiv + script))
    # return

    # print(__name__)
    helpers = pkg_resources.resource_string(resource_package, "helpers.js")
    script += helpers.decode("utf-8")

    multiple_choice = pkg_resources.resource_string(
        resource_package, "multiple_choice.js")
    script += multiple_choice.decode("utf-8")

    numeric = pkg_resources.resource_string(resource_package, "numeric.js")
    script += numeric.decode("utf-8")

    show_questions = pkg_resources.resource_string(
        resource_package, "show_questions.js")
    script += show_questions.decode("utf-8")

    if static:
        script += f"""
        {{
        show_questions(questions{div_id},  {div_id});
        }}
        </script>
        """
        javascript = script 


        print()
    else:
        script += f'''
        //console.log(element);
        {{
        const jmscontroller = new AbortController();
        const signal = jmscontroller.signal;

        setTimeout(() => jmscontroller.abort(), 5000);

        fetch("{url}", {{signal}})
        .then(response => response.json())
        .then(json => show_questions(json, {div_id}))
        .catch(err => {{
        console.log("Fetch error or timeout");
        show_questions(questions{div_id}, {div_id});
        }});
        }}
        </script>
        '''
        javascript = script 

    # print(javascript)
    display(HTML(mydiv + styles + javascript))
    #return div_id




def capture_responses(prev_div_id):
    '''

    This is prototype code only. I never got it work because the HTML that I
    update programmatically in this function is not preserved when the code is reloaded.
    For now, going to require the user to manually copy and paste their answer string to
    a new block.


    John  M. Shea
    7/25/2022
    '''
    resource_package = __name__

    letters = string.ascii_letters
    div_id = ''.join(random.choice(letters) for i in range(12))
    #print(div_id)

    mydiv = f"""<div id="{div_id}" ></div> """
    javascript= f"""
    <script type="text/Javascript">
        {{
    mydiv={div_id}
    nB_cell = mydiv.closest(".jp-Notebook-cell");
    //prev_cell = nb_cell.previousElementSibling.previousElementSibling;
    //prev_cell = document.getElementById({prev_div_id});
    prev_cell = {prev_div_id};
    console.log(prev_cell);
    responses = prev_cell.querySelector(".JCResponses");
    //console.log(responses);
    if (responses) {{
      //console.log(responses);
      mydiv.setAttribute("data-responses", responses.dataset.responses);
      //printResponses(mydiv); 
    var iDiv = document.createElement('div');
    iDiv.id = 'responses' + mydiv.id;
    iDiv.innerText=responses.dataset.responses;
    mydiv.appendChild(iDiv);
    }} else {{
      mydiv.setAttribute("data-responses", "[]");
      mydiv.innerText = 'No Responses Found';
    }}
       }}
    </script>
    """
    #print(mydiv)
    #print(javascript)
    display(HTML(mydiv + javascript))
    #display(Javascript(javascript))


    """
    var mydiv = {div_id};

    if (responses) {
      console.log(responses);
      mydiv.setAttribute("data-responses", responses.dataset.responses);
      printResponses(mydiv); 
    } else {
      mydiv.innerText = 'No Responses Found';
    }
    //var iDiv = document.createElement('div');
    //iDiv.id = 'responses' + mydiv.id;
    //iDiv.innerText=responses.dataset.responses;
    //mydiv.appendChild(iDiv);
 """
