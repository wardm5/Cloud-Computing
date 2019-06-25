import lombok.Data;
import java.util.List;
@Data
public class Forecast {
    String cod;
    double message;
    int cnt;
    List<WeatherWrapper> list;
}
