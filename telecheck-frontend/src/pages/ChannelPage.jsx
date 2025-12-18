import { useParams, Link } from "react-router-dom";
import { useState, useEffect } from "react";

function ChannelPage() {
  const { username } = useParams();
  const fullUsername = `t.me/${username}`;
  const [posts, setPosts] = useState([]);
  const [channelInfo, setChannelInfo] = useState(null);
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchChannelInfo = async () => {
      try {
        const res = await fetch("http://localhost:8000/analyze/channel-info", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ channels: [fullUsername] }),
        });
        const data = await res.json();
        setChannelInfo(data[0]);
      } catch (err) {
        console.error("Помилка при отриманні інформації про канал:", err);
      }
    };

    fetchChannelInfo();
  }, [fullUsername]);

  const handleFetchPosts = async () => {
    if (!startDate || !endDate) {
      alert("Оберіть період");
      return;
    }

    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/analyze/labeled-posts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          channels: [fullUsername],
          start_date: startDate,
          end_date: endDate,
        }),
      });

      const data = await res.json();
      setPosts(data);
    } catch (err) {
      alert("Помилка при отриманні постів");
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
        <div style={{ marginBottom: 20 }}>
          <Link to="/" style={{ textDecoration: "none", color: "#007bff" }}>
            ← Повернутись на головну
          </Link>
        </div>

        {channelInfo && (
          <div style={{ display: "flex", alignItems: "center", marginBottom: 20 }}>
            {channelInfo.photo_url && (
              <img
                src={`http://localhost:8000${channelInfo.photo_url}`}
                alt={channelInfo.title}
                width="40"
                height="40"
                style={{ borderRadius: "50%", marginRight: 10 }}
              />
            )}
            <h2 style={{ margin: 0 }}>{channelInfo.title}</h2>
          </div>
        )}

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
        <button onClick={handleFetchPosts} disabled={loading}>
          {loading ? "Аналізуємо..." : "Проаналізувати пости"}
        </button>

        <hr />
        <h2>Пости:</h2>
        {posts.length === 0 ? (
          <p>Немає постів для відображення</p>
        ) : (
          <ul>
            {posts.map((post, index) => (
              <li key={index}>
                <span
                  style={{
                    color: post.label === 1 ? "red" : "green",
                    fontWeight: "bold",
                  }}
                >
                  [{post.label === 1 ? "Шкідливий" : "Нормальний"}]
                </span>{" "}
                {post.post}
              </li>
            ))}
          </ul>
        )}
      </main>
    </div>
  );
}

export default ChannelPage;
