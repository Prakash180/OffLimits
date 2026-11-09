# Observer Pattern

> Category: **Behavioural** (defines a one-to-many dependency — when one object changes state, all its dependents get notified)

## What it is

- One object (the **Subject**/**Publisher**) maintains a list of dependents (**Observers**/**Subscribers**) and automatically **notifies** them whenever its state changes.
- Observers don't poll/ask repeatedly — they just get told when something happens.
- **Layman:** YouTube channel subscriptions. When a channel (Subject) uploads a new video, every subscriber (Observer) gets notified automatically — the channel doesn't need to know who exactly is subscribed, just that it needs to notify "everyone on the list".

## Why use it

- Decouples the Subject from its Observers — Subject only knows "a list of observers exist", not their concrete classes.
- Adding/removing observers at runtime is easy (`subscribe()` / `unsubscribe()`).
- Avoids manual polling ("keep checking if something changed") — notification is push-driven.

---

## Core Structure

```java
interface Observer {
    void update(String data);     // called by Subject when something changes
}

interface Subject {
    void subscribe(Observer o);
    void unsubscribe(Observer o);
    void notifyObservers();
}
```

---

## 1) Push Model

> The Subject sends the **full updated data** directly to each observer in the notification itself.

```java
import java.util.ArrayList;
import java.util.List;

class YouTubeChannel implements Subject {
    private List<Observer> subscribers = new ArrayList<>();
    private String latestVideoTitle;

    public void subscribe(Observer o) { subscribers.add(o); }
    public void unsubscribe(Observer o) { subscribers.remove(o); }

    public void uploadVideo(String title) {
        this.latestVideoTitle = title;
        notifyObservers();                 // state changed -> push it out immediately
    }

    public void notifyObservers() {
        for (Observer o : subscribers) {
            o.update(latestVideoTitle);     // pushing the actual data directly
        }
    }
}

class Subscriber implements Observer {
    private String name;
    Subscriber(String name) { this.name = name; }

    public void update(String videoTitle) {
        // data arrives directly in the call, no need to ask the Subject for anything else
        System.out.println(name + " notified: New video -> " + videoTitle);
    }
}

// Client code
YouTubeChannel channel = new YouTubeChannel();
Subscriber alice = new Subscriber("Alice");
Subscriber bob = new Subscriber("Bob");

channel.subscribe(alice);
channel.subscribe(bob);

channel.uploadVideo("Observer Pattern Explained");
// -> Alice notified: New video -> Observer Pattern Explained
// -> Bob notified: New video -> Observer Pattern Explained
```

- **Push model:** `update(String videoTitle)` — the Subject decides exactly what data to send, and hands it straight to the observer.
- **Pro:** Simple, observer doesn't need a reference back to the Subject.
- **Con:** If the Subject later has more data fields (views, duration, etc.), the `update()` method signature keeps growing, and observers get data they might not even need.

---

## 2) Pull Model

> The Subject only sends a lightweight notification ("something changed"); the observer then **pulls** whatever specific data it needs from the Subject itself.

```java
import java.util.ArrayList;
import java.util.List;

interface Observer {
    void update(Subject subject);     // gets a reference to the Subject, not the data itself
}

interface Subject {
    void subscribe(Observer o);
    void unsubscribe(Observer o);
    void notifyObservers();
}

class YouTubeChannel implements Subject {
    private List<Observer> subscribers = new ArrayList<>();
    private String latestVideoTitle;
    private int latestViews;

    public void subscribe(Observer o) { subscribers.add(o); }
    public void unsubscribe(Observer o) { subscribers.remove(o); }

    public void uploadVideo(String title) {
        this.latestVideoTitle = title;
        this.latestViews = 0;
        notifyObservers();
    }

    public void notifyObservers() {
        for (Observer o : subscribers) {
            o.update(this);               // pushing only a reference, NOT the actual data
        }
    }

    // getters — observers "pull" data through these
    public String getLatestVideoTitle() { return latestVideoTitle; }
    public int getLatestViews() { return latestViews; }
}

class Subscriber implements Observer {
    private String name;
    Subscriber(String name) { this.name = name; }

    public void update(Subject subject) {
        // observer decides what it actually needs, and pulls just that
        YouTubeChannel channel = (YouTubeChannel) subject;
        System.out.println(name + " notified: New video -> " + channel.getLatestVideoTitle());
    }
}

// Client code
YouTubeChannel channel = new YouTubeChannel();
Subscriber alice = new Subscriber("Alice");

channel.subscribe(alice);
channel.uploadVideo("Pull Model Example");
// -> Alice notified: New video -> Pull Model Example
```

- **Pull model:** `update(Subject subject)` — observer receives a reference to the Subject and calls getters to pull exactly the fields it cares about.
- **Pro:** Flexible — adding new fields to the Subject doesn't break the `update()` signature; each observer only pulls what it needs.
- **Con:** Slightly more coupling — observer needs to know the Subject's public API (getters) to pull data; a bit more work per notification (method calls instead of direct data).

---

## Push vs Pull — Quick Comparison

| Aspect | Push Model | Pull Model |
|---|---|---|
| What's sent in notification | Actual data directly | Just a reference to the Subject |
| Observer effort | None — data handed to it | Must call getters to fetch what it needs |
| Coupling | Observer doesn't need Subject's API | Observer needs to know Subject's getters |
| Flexibility if Subject grows | `update()` signature may need to change | `update()` signature stays the same |
| Risk | Observer may get irrelevant/excess data | Observer must know what to ask for |

---

## When to use it

- Event-driven systems: UI listeners (button clicks), pub-sub systems, messaging queues, real-time feeds (stock prices, notifications).
- Anytime multiple parts of a system need to react to a change in one place without tight coupling.

## Pitfalls

- If observers are never unsubscribed, can cause **memory leaks** (Subject holds references forever — this is the classic "lapsed listener" problem).
- Notification order isn't guaranteed unless explicitly managed — don't rely on which observer gets notified first.
- Chains of observers notifying other observers can get hard to debug ("notification storms").

## Quick Recap

| Aspect | Detail |
|---|---|
| Purpose | One-to-many notification — Subject tells all Observers when its state changes |
| Key trick | Subject keeps a list of Observers; calls a common `update()` method on each |
| Push model | Subject sends full data directly in `update(data)` |
| Pull model | Subject sends itself/a reference in `update(subject)`; observer pulls what it needs via getters |
| Watch out for | Memory leaks from forgotten unsubscribes, unpredictable notification order |
