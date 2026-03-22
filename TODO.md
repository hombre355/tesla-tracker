# Tesla Tracker — Feature Roadmap

Inspired by [TeslaMate](https://github.com/teslamate-org/teslamate). Items are grouped by category and roughly ordered by value vs. effort.

---

## 🔋 Battery & Range

- [ ] **Battery health tracking** — record rated range over time to visualize degradation trend
- [ ] **Projected range chart** — plot estimated vs. ideal range over the vehicle's lifetime
- [ ] **Usable vs. total battery** — distinguish between usable capacity and total pack size
- [ ] **Vampire drain tracking** — record energy lost while parked (delta kWh between drive end and next drive start)

---

## 🗺️ Location & Maps

- [ ] **Trip route map** — display the driven route on a map for each trip (requires storing GPS breadcrumbs during drives, not just start/end)
- [ ] **Lifetime driving map** — heatmap or polyline of all drives on a single map
- [ ] **Geofencing / location labels** — tag locations (Home, Work, Supercharger, etc.) so trips and charges show human-readable names instead of coordinates
- [ ] **Reverse geocoding** — convert GPS coordinates to street addresses for trip start/end
- [ ] **Visited locations list** — show all unique charging/parking locations with visit counts

---

## 📊 Trip Enhancements

- [ ] **Elevation tracking** — record ascent and descent during each trip; factor into efficiency analysis
- [ ] **Speed histogram** — distribution of speeds driven per trip or overall
- [ ] **Idle time tracking** — time spent parked with climate on between drives
- [ ] **Trip filtering** — filter out very short drives (configurable minimum duration/distance)

---

## ⚡ Charging Enhancements

- [ ] **Charge curve visualization** — plot kW vs. time for each charging session
- [ ] **Home vs. away charging split** — monthly breakdown of home kWh vs. public/Supercharger kWh
- [ ] **Geofence-based cost rates** — assign different electricity rates to different locations (e.g., home vs. work)
- [ ] **Consecutive charge detection** — identify and optionally exclude solar/PV surplus charging sessions
- [ ] **Charging heatmap** — time-of-day heatmap showing when the car is typically charged

---

## 🚗 Vehicle Status & Health

- [ ] **Real-time vehicle status** — live display of online/asleep/driving/charging state on dashboard
- [ ] **Software version history** — track Tesla firmware updates with dates
- [ ] **Tire pressure monitoring (TPMS)** — display current tire pressures when available from API
- [ ] **Climate/preconditioning log** — record when climate was running and energy cost

---

## 🔔 Alerts & Notifications

- [ ] **Charging complete notification** — push/email alert when charging session ends
- [ ] **Low battery alert** — notify when battery drops below a configurable threshold
- [ ] **Token expiry warning** — alert in the UI when the refresh token is close to expiring (prompt to re-paste)
- [ ] **Update available notification** — detect new Tesla firmware and notify

---

## 📤 Data & Integrations

- [ ] **CSV export** — export trips, charges, and stats to CSV for use in Excel/Sheets
- [ ] **MQTT publishing** — publish live vehicle data to a local MQTT broker for Home Assistant / automations
- [ ] **Home Assistant integration** — MQTT-based sensors for battery %, charge state, odometer
- [ ] **Webhook support** — send events (trip end, charge complete) to a configurable URL

---

## 📈 Analytics & Reporting

- [ ] **Monthly summary report** — auto-generated monthly digest (total miles, kWh, cost, savings)
- [ ] **Year-over-year comparison** — compare current year vs. previous year for key metrics
- [ ] **Cumulative odometer chart** — lifetime mileage trend
- [ ] **Cost per mile tracking** — electricity cost divided by miles driven, trended over time
- [ ] **Efficiency by weather/temperature** — correlate efficiency with ambient temperature

---

## 🎨 UI & Experience

- [ ] **Dark / light theme toggle** — user-selectable theme (currently dark only)
- [ ] **Mobile-optimized layout** — improve responsiveness for phone-sized screens
- [ ] **PWA / installable app** — add web app manifest so it can be installed on home screen
- [ ] **Real-time dashboard auto-refresh** — live updates without manual refresh when car is active
- [ ] **Configurable dashboard widgets** — let user choose which stats appear on the dashboard

---

## 🔧 Infrastructure & Reliability

- [ ] **Streaming API support** — use Tesla's streaming endpoint instead of polling for higher-resolution trip data and less battery drain
- [ ] **Retry / circuit breaker** — stop hammering API when vehicle is unreachable; back off gracefully
- [ ] **API rate limit handling** — detect 429 responses and implement exponential backoff
- [ ] **Database backup** — scheduled pg_dump to a local file or S3-compatible storage
- [ ] **Multi-vehicle UI** — proper vehicle switcher when more than one Tesla is connected
