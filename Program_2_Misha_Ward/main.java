import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLEncoder;
import java.util.*;
import com.google.gson.Gson;
import java.text.SimpleDateFormat;
import java.util.Date;

     /************************************************************************
     *                                                                       *
     *                 -- Weather App Program by Misha Ward --               *
     *       Program asks for user for city and then provides 5 day          *
     *       forecast for that city. It also provides windspeed for that     *
     *       day. The program handles incorrect inputs by providing          *
     *       the user error message and promoting them to provide a new      *
     *       input or to exit the program.                                   *
     *                                                                       *
     ************************************************************************/

public class main {
    private final static String degSymbol  = "\u00b0";  // degree symbol
    public static void main(String[] args) throws Exception {
        Scanner scan = new Scanner (System.in);    // scanner object for user input
        start(scan);                               // starting text
    }

    private static void start(Scanner scan) throws Exception {  // start method, helps printout some information
        System.out.println("Hello there, this is the simple weather report. \n");
        boolean check = true;  // set boolean check to true
        do {
            if (check) {
                System.out.print("Please enter in a city, otherwise enter \"exit\".  " );
            }
            String city = URLEncoder.encode(scan.nextLine().toLowerCase(), "UTF-8");  // encodes string to url standard
            if (city.equals("exit")) {  // if city equals "exit"
                System.out.println("\nGood bye! ");  // then tell user goodbye
                return;  // exit program
            }
            String url = "http://api.openweathermap.org/data/2.5/forecast?q=" + city + "&APPID=b351e40979955f1a541e74a6c4da057a";  // url for api
            HttpURLConnection con = sendGet(url);       // sets up Http connection to website
            String json = getWebsiteString(con);        // get website string (api json)
            if (json == null) {  // if returned json is null
                check = false;  // switch boolean to false
                continue;  // reset loop
            }
            int response = getResponseCode(con);        // gets the response of the website
            con.disconnect();                           // disconnects from website
            Forecast forecast = getForecastFromResponse(json);  // get forecast object from json
            int count = 1;  // set count for day
            System.out.println("\nBelow is the weather for " + city.toUpperCase() + ": ");
            for (int i = 0; i < forecast.getList().size(); i++) {  // for each 3 hour forecast
                String dtStr = forecast.getList().get(i).getDt_txt();  // gets date text
                Date date = new SimpleDateFormat("yyyy-MM-dd").parse(dtStr);  // sets the date to a pattern
                SimpleDateFormat dayOfWeek = new SimpleDateFormat("EEEE, MMM dd");  // re-organizes pattern to another pattern
                String temp = String.format("%.1f", conversion(forecast.getList().get(i).getMain().getTemp()));  // sets temp variable
                String windSpeed = String.format("%.1f", forecast.getList().get(i).getWind().getSpeed());  // sets windspeed variable
                System.out.print("The temp for " + dayOfWeek.format(date) + ", will be " + temp + degSymbol);  // prints info
                System.out.println(", the windspeed will be " + windSpeed + "m/s. ");   // prints more info
                count++;
                i = i + 7;  // ensures that weather is given for each day
            }
            check = false;
            System.out.print("\nPlease enter in a city, otherwise enter \"exit\".  " );
        } while (scan.hasNext());
    }

    // HTTP GET request, sets up link to website
    private static HttpURLConnection sendGet(String url) throws Exception {
        URL obj = new URL(url);
        HttpURLConnection con = (HttpURLConnection) obj.openConnection();
        con.setRequestMethod("GET");
        return con;
    }

    // WEBSITE STRING method, returns string of website
    private static String getWebsiteString(HttpURLConnection con) throws Exception{
        StringBuilder result = new StringBuilder();  // new string builder
        if (con.getResponseCode() > 200) {  // check if response code is greater than 200
            System.out.print("NOTE: Error with connection, city was not valid. \n\nPlease enter in a city, otherwise enter \"exit\".  ");
            return null;  // return null if response > 200
        }
        BufferedReader rd = new BufferedReader(new InputStreamReader(con.getInputStream()));  // buffered reader
        String line;  // generic line
        while ((line = rd.readLine()) != null) {  // while buffered reader has a lines that are not null
            result.append(line + "\n");  // append the string builder
        }
        rd.close();  // close buffer reader
        return result.toString();  // return string
    }

    // RETURN RESPONSE CODE, gets the response code of website
    private static int getResponseCode(HttpURLConnection con) throws Exception {
        int code = con.getResponseCode(); // returns response code
        return code;
    }

    // RETURN FORECAST, returns the forecast class from the json
    private static Forecast getForecastFromResponse(String data) {
        return new Gson().fromJson(data, Forecast.class);  // returns Forecast object
    }

   // CONVERTS TEMP, returns the converted temp from kelvin to fahrenheit
    private static double conversion(double temp) {
        return ( ((temp - 273.15) * (9.0/5.0)) + 32);  // returns converted temp from kelvin to fahrenheit
    }
}
