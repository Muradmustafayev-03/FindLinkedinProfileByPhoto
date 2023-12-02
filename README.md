# FindLinkedinProfileByPhoto

Imagine that you are at a tech conference, taking pictures / selfies with people you meet during the event. Now, imagine that you look at the picture and tap on the person on that photo and you don’t remember his name or his contact details. This program implements face detection and recognition to find a linkedin profile of a person by photo.

## How to run
*Recommended to run on Linux.*

_**Note:** the program uses `dlib` library, that relies on `c++` code, which would require `Visual Studio Build Tools` installed on your machine if you want to run it on Windows._

### To run the program, proceed the following steps:
1. Clone this repository
2. Run `pip install -r requirements.txt` in your terminal
3. Create a `secret.py` file with 2 constants:
   * `USERNAME` (str) - your LinkedIn username
   * `PASSWORD` (str) - your LinkedIn password

   *__Note:__ Indeed, these constants can also be declared in the `main.py` file of the client folder*

4. In the `main.py` file of the client folder specify the path to your photo and other parameters

