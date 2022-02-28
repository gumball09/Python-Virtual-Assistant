# PYTHON VIRTUAL ASSISTANT

This virtual assistant is designed with simplicity in mind, which performs basic functionalities that assist users in their daily lives

### Setup
- Clone this repo
- Create a virtual environment: `python3 -m venv <path_to_virtual_env>` (`python3 -m venv myenv/.`)
- Download the required packages: `pip install -r requirements.txt` <br/>
__Make sure to have `SpeechRecognition`, `PyAudio` and `pyttsx3` installed for the skeleton to function__

#### To get Weather Data
- Create an account at [openweathermap.org](https://openweathermap.org)
- Create an API key and replace `configs["WEATHER_API_KEY"]` with your own

### Important Notes
- Some of the imports are explicitly imported to suppress warnings and errors. These do not affect the flow of the virtual assistant as some imports are device-dependant.