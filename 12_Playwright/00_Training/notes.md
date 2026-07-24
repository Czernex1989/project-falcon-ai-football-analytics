const = tworzę zmienną, której później nie przypisuję nowej wartości
let = tworzę zmienną, której wartość może się zmienić
if = sprawdzam warunek
console.log() = pokazuję wynik w konsoli
chromium.launch() = uruchamia przeglądarkę
browser.newPage() = tworzy nową kartę
page.goto(web) = otwiera stronę
browser.close() = zamyka przeglądarkę

const web = "https://realmadrid.pl";

Zapisuje adres strony pod nazwą web.

await page.goto(web);

Otwiera stronę zapisaną w web i czeka na wykonanie operacji.

const title = await page.title();

Pobiera tytuł strony, czeka na wynik i zapisuje go pod nazwą title.

console.log(title);

Pokazuje tytuł w konsoli.

const heading = await page.locator("h1").textContent();

Znajduje nagłówek h1, pobiera jego tekst i zapisuje go pod nazwą heading.

console.log(heading);

Pokazuje tekst nagłówka w konsoli.

await page.getByRole("link", { name: "Aktualności" }).click();

Znajduje link „Aktualności”, klika go i czeka na wykonanie kliknięcia.

await page.getByRole("textbox").fill("Real Madrid");

Znajduje pole tekstowe i wpisuje do niego „Real Madrid”.