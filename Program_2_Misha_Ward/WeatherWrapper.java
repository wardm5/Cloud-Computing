import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;
import java.util.List;

@Data
public class WeatherWrapper {
    private Cord coord;
    private List<Weather> weather;
    private String base;
    private MainObj main;
    private double visibility;
    private Wind wind;
    private Clouds clouds;
    private long dt;
    private Sys sys;
    private int id;
    private String name;
    private int cod;
//    @JsonProperty("dt_txt")
    private String dt_txt;
}
