import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import "../styles/HomePage.css";

function HomePage() {
  const [channels, setChannels] = useState([]);
  const [selectedChannels, setSelectedChannels] = useState([]);
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetch("http://localhost:8000/analyze/channel-info", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        channels: [
          "t.me/kievinfo_kyiv",
          "t.me/Tsaplienko",
          "t.me/lachentyt",
          "t.me/truexanewsua",
          "t.me/novinach",
          "t.me/SK_DM_SK",
          "t.me/kpszsu",
          "t.me/ukrnastup",
          "t.me/milinua",
          "t.me/football20ua",
          "t.me/UaOnlii",
          "t.me/oko_ua",
          "t.me/ssternenko",
          "t.me/k_dvizh",
          "t.me/OP_UA",
          "t.me/oleksiihoncharenko",
        ],
      }),
    })
      .then((res) => res.json())
      .then((data) => setChannels(data))
      .catch((err) => console.error("Помилка завантаження каналів:", err));
  }, []);

  const toggleChannel = (channelUsername) => {
    setSelectedChannels((prev) =>
      prev.includes(channelUsername)
        ? prev.filter((ch) => ch !== channelUsername)
        : [...prev, channelUsername]
    );
  };

  const handleAnalyze = async () => {
    if (selectedChannels.length === 0 || !startDate || !endDate) {
      alert("Оберіть канали та дати!");
      return;
    }

    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/analyze/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          channels: selectedChannels,
          start_date: startDate,
          end_date: endDate,
        }),
      });

      const data = await res.json();
      setResults(data);
    } catch (err) {
      alert("Помилка при аналізі");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-root">
      <header className="top-bar">
        TeleCheck
      </header>

      <main className="content">
        <p>Аналіз шкідливості постів у Telegram-каналах</p>

        <form onSubmit={(e) => e.preventDefault()}>
          <h2>Оберіть канали:</h2>
          {channels.map((channel) => (
            <div key={channel.username} style={{ display: "flex", alignItems: "center", marginBottom: 8 }}>
              <input
                type="checkbox"
                checked={selectedChannels.includes(channel.username)}
                onChange={() => toggleChannel(channel.username)}
              />
              {channel.photo_url && (
                <img
                  src={`http://localhost:8000${channel.photo_url}`}
                  alt={channel.title}
                  width="30"
                  height="30"
                  style={{ borderRadius: "50%", margin: "0 10px" }}
                />
              )}
              <Link
                to={`/channel/${channel.username.replace("t.me/", "")}`}
                style={{ textDecoration: "none", color: "black", marginLeft: 8 }}
              >
                {channel.title}
              </Link>
            </div>
          ))}

          <h2>Виберіть період:</h2>
          <label>
            Початкова дата:
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
            />
          </label>
          <br />
          <label>
            Кінцева дата:
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
            />
          </label>
          <br />
          <button type="button" onClick={handleAnalyze} disabled={loading}>
            {loading ? "Аналізуємо..." : "Аналізувати"}
          </button>
        </form>

        <hr />
        <h2>Результати:</h2>
        <ul>
          {results.map((res) => {
            const matchedChannel = channels.find((ch) => ch.username === res.channel);
            const displayTitle = matchedChannel ? matchedChannel.title : res.channel;

            return (
              <li key={res.channel}>
                <strong>{displayTitle}</strong>: {res.harmful_percent}% шкідливих ({res.harmful} / {res.harmful + res.normal})
              </li>
            );
          })}
        </ul>
      </main>
    </div>
  );
}

export default HomePage;
