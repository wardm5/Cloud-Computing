import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

@Data
public class MainObj {
    private double temp;
    private double pressure;
    private double humidity;
    private double temp_min;
    private double temp_max;
    @JsonProperty("sea_level")
    private double seaLevel;
    @JsonProperty("grnd_level")
    private double grndLevel;
    @JsonProperty("temp_kf")
    private double tempKf;
}
