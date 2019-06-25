import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.*;
import java.util.regex.Pattern;
import java.util.regex.Matcher;
import java.net.MalformedURLException;

    /************************************************************************
    *                                                                       *
    *                 -- Web crawler Program by Misha Ward --               *
    *       Program starts with url and looks for other websites to go      *
    *       to based on hops given by user. Uses regex pattern matcher      *
    *       to search for new websites.                                     *
    *       Handles 200 (OK) and 300 codes (redirects).                     *
    *                                                                       *
    ***********************************************************************/

public class main {
    public static void main(String[] args) throws Exception {
        String url = args[0];                           // starting website
        int hops = Integer.parseInt( args[1] );         // starting hops
        start(url, hops);                               // starting text
        HashSet<String> set = new HashSet();            // set to make sure dont visit the same website
        addUrl(url, set);                               // adds to set
        String response  = webCrawler(url, hops, set);  // calls webcrawl
        System.out.println(response);                   // prints final html
    }

    private static void start(String url, int hops) throws Exception {  // start method, helps printout some information
        System.out.println("Hello there, this is the simple webcrawler. ");
        System.out.println("Current defaults for this website is " + url + " and hops is set to " + hops + ". ");
        System.out.println("\n--------------------------------------- HTML Links Below ---------------------------------------");
        HttpURLConnection con = sendGet(url);       // sets up Http connection to website
        int response = getResponseCode(con);        // gets the response of the website
        con.disconnect();                           // disconnects from website
        System.out.println("Original Url: " + url + ". ");
        System.out.println("Response code: " + response);
    }

    private static String webCrawler(String url, int hops, HashSet<String> set) throws Exception {
        String prior = "";  // prior website url
        String priorWebsiteString = "";  // string for prior website
        String websiteString = "";  // string for final website
        int count = 1;  // counting the hops
        for (int i = 0; i <= hops; i++) {
            try {
                HttpURLConnection con = sendGet(url);  // setup connection to website
                int response = getResponseCode(con);   // get response code
                websiteString = getWebsiteString(con); // get website string
                con.disconnect();                      // disconnect from site
                prior = url;                           // set prior website to the url
                if (response >= 200 && response < 300 && i <= hops) {  // if response code within 2XX
                    List<String> list = regExFunction(websiteString);  // create list of all urls within body of the site
                    for (int j = 0; j < list.size(); j++) {            // for each url, loop
                        if (!set.contains(list.get(j)) && i != 0) {    // if the set does not contains the url
                            prior = url;                               // set prior to url
                            priorWebsiteString = websiteString;        // set prior website to website
                            url = list.get(j);                         // set url to the website in the list
                            addUrl(url, set);                          // add the url to the set
                            con = sendGet(url);                        // setup connection for website
                            response = getResponseCode(con);           // get response code for website
                            if (response >= 300 && response < 400) {   // if website is a redirect...
                                String redirectUrl = con.getHeaderField("Location");  // set website to the header
                                System.out.println("Hop " + count + ", Redirect url: " + url + " -> " + redirectUrl);
                                System.out.println("Response code: " + response);
                                i = count;                             // set i to count
                            } else {
                                System.out.println("Hop " + count + " is url: " + url + ".");  // else print useful info
                                System.out.println("Response code: " + response);
                                i = count;
                                count++;
                            }
                            if (i == hops) {  // if i equals the amount of hops
                                System.out.println();  // then add extra line
                            }
                            con.disconnect();  // disconnect from website
                            break;
                        }
                    }
                } else if (response >= 300 && response < 400 && i <= hops) {  // if website is redirect
                    if (response == HttpURLConnection.HTTP_MOVED_TEMP
                            || response == HttpURLConnection.HTTP_MOVED_PERM) {
                        url = con.getHeaderField("Location");  // set url to the header
                        i = count;
                        count++;
                    }
                }
            } catch (MalformedURLException e) {  // catches links that are not written correctly
                System.out.println("\nThe last url was malformed: " + url);
                System.out.println("Because the last hop was malformed link, the last working website is: " + prior);
                System.out.println("--------------------------------------- HTML String Below --------------------------------------");
                return priorWebsiteString;
            } catch (Exception e) {  // general exception to catch all other errors
                System.out.println("\nBecause the last hop was not a working link, the last working website is: " + prior);
                System.out.println("--------------------------------------- HTML String Below --------------------------------------");
                return websiteString;
            }
        }
        System.out.println("--------------------------------------- HTML String Below --------------------------------------");
        return priorWebsiteString;
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
        int code = con.getResponseCode();
        return code;
    }

    // REGEX FUNCTION, uses regex to parse HTML String to find next websites
    private static List<String> regExFunction(String input) {
        Pattern p = Pattern.compile("a href=\"(.*?)\"");    // creates pattern on body href tags
        Matcher m = p.matcher(input);                       // creates matcher
        List<String> regExList = new ArrayList<>();         // creates new ArrayList
        while (m.find()) {                                  // while matcher finds links
            regExList.add(m.group(1));                      // add link to the ArrayList
        }
        return regExList;       // return ArrayList of websites
    }

    // ADD URL, adds urls to the set
    private static void addUrl(String url, HashSet set) {
        if (url.charAt(url.length()-1) == '/') {        // if url ends with '/'
            set.add(url);                               // add the url
            set.add(url.substring(0,url.length()-1));   //add the url without the '/'
        } else {
            set.add(url);                               // add url (without '/')
            set.add(url + '/');                         // add url with '/'
        }
    }
}