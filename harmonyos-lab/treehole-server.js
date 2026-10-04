/**
 * 回声树洞 · 匿名树洞持久化 API（零依赖，Node 18+）
 * GET  /treehole          → 帖子列表（新→旧）
 * POST /treehole          → {content} 匿名发帖
 * POST /treehole/like     → {id, action: 'like'|'unlike'} 点赞/取消
 * 数据落盘：treehole.json（重启不丢）
 */
const http = require('http');
const fs = require('fs');
const path = require('path');

const DB_FILE = path.join(__dirname, 'treehole.json');
const PORT = 3001;

function load() {
  try {
    return JSON.parse(fs.readFileSync(DB_FILE, 'utf-8'));
  } catch (e) {
    return [];
  }
}

function save(list) {
  fs.writeFileSync(DB_FILE, JSON.stringify(list, null, 1), 'utf-8');
}

function anonName() {
  return '洞友 #' + (1000 + Math.floor(Math.random() * 9000));
}

function now() {
  const d = new Date(Date.now() + 8 * 3600 * 1000);
  return d.toISOString().replace('T', ' ').substring(5, 16);
}

const server = http.createServer((req, res) => {
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  res.setHeader('Access-Control-Allow-Origin', '*');

  if (req.method === 'GET' && req.url.startsWith('/treehole')) {
    const list = load().sort((a, b) => b.id - a.id);
    res.end(JSON.stringify({ code: 200, posts: list }));
    return;
  }

  if (req.method === 'POST' && req.url.startsWith('/treehole/like')) {
    let body = '';
    req.on('data', (c) => (body += c));
    req.on('end', () => {
      try {
        const { id, action } = JSON.parse(body || '{}');
        const list = load();
        const post = list.find((p) => p.id === id);
        if (!post) {
          res.statusCode = 404;
          res.end(JSON.stringify({ code: 404, msg: 'post not found' }));
          return;
        }
        post.likes += action === 'unlike' ? -1 : 1;
        post.liked = action !== 'unlike';
        if (post.likes < 0) post.likes = 0;
        save(list);
        res.end(JSON.stringify({ code: 200, post }));
      } catch (e) {
        res.statusCode = 400;
        res.end(JSON.stringify({ code: 400, msg: e.message }));
      }
    });
    return;
  }

  if (req.method === 'POST' && req.url.startsWith('/treehole')) {
    let body = '';
    req.on('data', (c) => (body += c));
    req.on('end', () => {
      try {
        const { content } = JSON.parse(body || '{}');
        const text = (content || '').trim();
        if (!text) {
          res.statusCode = 400;
          res.end(JSON.stringify({ code: 400, msg: 'content empty' }));
          return;
        }
        const list = load();
        const post = {
          id: Date.now(),
          author: anonName(),
          content: text.substring(0, 200),
          time: now(),
          likes: 0,
          liked: false
        };
        list.push(post);
        save(list);
        res.end(JSON.stringify({ code: 200, post }));
      } catch (e) {
        res.statusCode = 400;
        res.end(JSON.stringify({ code: 400, msg: e.message }));
      }
    });
    return;
  }

  res.statusCode = 404;
  res.end(JSON.stringify({ code: 404, msg: 'not found' }));
});

server.listen(PORT, () => {
  console.log(`[treehole] listening on http://0.0.0.0:${PORT}`);
});
