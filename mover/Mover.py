

class Mover:
    def __init__(self, browser):

        self.browser = browser

    def move(self, action):
        allowed_keybinds = ('w', 's', 'd', 'a')
        key = allowed_keybinds[action]

        key_map = {
            "up": "ArrowUp",
            "down": "ArrowDown",
            "left": "ArrowLeft",
            "right": "ArrowRight",
            "w": "KeyW",
            "a": "KeyA",
            "s": "KeyS",
            "d": "KeyD"
        }

        if key in key_map:
            js_code = f'''
             var event = new KeyboardEvent('keydown', {{
                 key: '{key_map[key]}',
                 code: '{key_map[key]}',
                 keyCode: {ord(key_map[key][-1])}, 
                 which: {ord(key_map[key][-1])}, 
                 bubbles: true 
             }});
             document.dispatchEvent(event);
             '''
            self.browser.execute_script(js_code)

