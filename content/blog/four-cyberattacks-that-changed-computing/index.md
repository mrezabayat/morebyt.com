---
title: "From Brain to Equifax: 4 cyberattacks that changed computing"
description: How the Brain virus, the Morris worm, ILOVEYOU and the Equifax breach worked, why each one spread, and what it changed for the people who build software.
date: 2026-04-18
updated: 2026-11-20
tags: security, history
---

Old security incidents tend to blur into one story of "a virus, a worm, a breach". The four below failed in different ways, though, and each one taught the industry something different. Brain spread on floppy disks people swapped by hand. The Morris worm used bugs in network services to cross the early internet in a night. ILOVEYOU got people to run it themselves. Equifax was a known, patchable vulnerability that stayed open for months inside a company holding personal data on millions of people.

What they have in common is trust: a disk from a colleague, a host on the same network, an email from a friend, a server nobody checked. Each attack took something people trusted and used it to spread.

![Timeline of Brain, Morris, ILOVEYOU, and Equifax](timeline.svg)

| Incident | Date | Type | How it got in | Immediate impact |
| --- | --- | --- | --- | --- |
| Brain | 19 January 1986 (commonly cited) | Boot-sector virus | Infected floppy disks | One of the first worldwide virus scares on IBM PC compatibles |
| Morris worm | 2 November 1988 | Internet worm | `sendmail`, `fingerd`, trusted hosts, weak passwords | About 6,000 of roughly 60,000 internet machines hit within a day |
| ILOVEYOU | 4 May 2000 | Mass-mailing worm | Email attachment sent to every Outlook contact | Mail systems overloaded; many organisations shut their email gateways |
| Equifax | Attack from 13 May 2017; disclosed 7 September 2017 | Data breach | Unpatched Apache Struts flaw, then web shells and stored credentials | Data on about 143 million people exposed, a figure later revised upward |

## Brain (1986): the virus that travelled by hand

Brain is usually described as the first major virus on IBM PC compatibles. Historical summaries date its release to 19 January 1986 and credit it to two brothers in Lahore, Pakistan, Basit and Amjad Farooq Alvi.

It was a boot-sector virus. When a PC started from an infected floppy, the virus loaded before the operating system, copied itself into memory and then infected other floppies used on that machine. It also moved the original boot sector elsewhere on the disk, an early trick to make the infection harder to spot.

![Illustration of a floppy disk used to spread the Brain virus](brain-floppy.svg)

In 1986 a floppy was storage, software distribution and file sharing all at once, and nobody scanned a disk that came from a colleague or a classmate. Brain didn't need to destroy anything to matter. It showed that the PC market had grown big enough for a virus to travel far from where it started, and it helped turn antivirus software from a curiosity into a product category.

The lesson still holds: if people routinely pass something around, attackers will eventually use it to pass malware around too.

## The Morris worm (1988): one program, a whole network

On 2 November 1988, at about 8:30 in the evening, a worm was released onto the internet from a machine at MIT. According to the FBI's case summary, an estimated 6,000 of the roughly 60,000 computers then on the internet were affected within 24 hours.

![Diagram showing how the Morris worm spread across early networked Unix systems](morris-worm-network.svg)

The worm had several ways in. It used a flaw in `sendmail`, a buffer overflow in the `fingerd` service, the trust relationships between Unix hosts, and password guessing against weak accounts. If one route failed, another often worked.

The damage came from a design mistake rather than a payload. Machines could claim to be infected already to keep the worm out, so the worm sometimes copied itself anyway. Copies piled up on the same hosts until they slowed to a crawl or crashed, and some sites cut themselves off the network while they worked out how to stop reinfection. Nothing was deliberately destroyed; the machines simply ran out of resources.

The incident is closely tied to the creation of CERT/CC and a more formal approach to coordinated incident response, and it led to the first felony conviction under the U.S. Computer Fraud and Abuse Act. It also ended the idea that a network of universities and labs could be left to police itself.

The `fingerd` bug is worth knowing in detail: the service read input into a fixed-size buffer without checking its length, which let the worm overwrite the stack. I explain how that kind of bug works in a video on buffer overflows coming to [the Morebyt channel](https://www.youtube.com/@morebyt) in December 2026. The general lesson is that automated code spreads a small mistake across a network faster than people can react.

## ILOVEYOU (2000): getting people to run it

The ILOVEYOU worm, also called Love Letter, started spreading on 4 May 2000. It arrived with a personal-looking subject line and an attachment called `LOVE-LETTER-FOR-YOU.TXT.vbs`.

![Illustration of the ILOVEYOU email lure and address-book spread](iloveyou-email.svg)

Windows hid known file extensions by default, so many people saw a harmless `.TXT` file and not the `.vbs` script it really was. Once opened, the script mailed itself to every contact in the victim's Outlook address book, from the victim's own account, as Microsoft's malware write-up describes. It also copied itself onto the machine, changed settings, and was reported in many analyses to overwrite files and try to download a password-stealing component.

The trick was that the message came from someone you knew. People trusted email from friends and colleagues, and the worm used exactly that trust. No clever exploit was needed once the dangerous action looked like an ordinary one.

Many companies and government organisations shut down or filtered their email systems just to slow it down. Afterwards, mail filters started blocking script attachments, email security and endpoint security started working together, and user training began to cover file extensions and lures. If an attack rides on people's normal routine, telling them to be careful is not a defence.

## Equifax (2017): a known bug, left open

Equifax is a modern failure, and the public record is detailed enough to follow it step by step. According to the U.S. House Oversight Committee's staff report, a critical vulnerability in the Apache Struts web framework was disclosed on 7 March 2017. Equifax was alerted and told its teams to patch, but one internet-facing system, its dispute portal ACIS, stayed unpatched.

![Diagram of the Equifax breach chain from missed patch to public disclosure](equifax-breach.svg)

Attackers started exploiting it on 13 May 2017. The report describes them installing web shells to keep access, finding unencrypted credentials, and using those to reach databases beyond the first system. Equifax's monitoring didn't catch them because a certificate on a traffic-inspection device had expired, leaving that traffic unchecked for 19 months. The company noticed suspicious activity on 29 July and disclosed the breach on 7 September 2017.

At disclosure, Equifax said about 143 million U.S. consumers were affected, and later revised the number upward. The data included names, Social Security numbers, birth dates, addresses and some driver's licence numbers, plus smaller sets of card numbers and dispute documents. Unlike a password, a Social Security number can't be changed, so the damage lasts.

Nothing here was a mysterious zero-day. Patching, asset inventory, certificate management, network segmentation and monitoring each failed, one after another. The breach became the standard example of why those dull controls matter, and of why a company holding data that people never chose to give it needs to protect that data especially well.

## What the four have in common

Each incident matches its era. Brain used the medium people shared work on. Morris used a network that trusted its members. ILOVEYOU used people and their email clients as the delivery system. Equifax used an organisation that had stopped noticing its own gaps. Computing became more connected and more layered over those thirty years, and each era kept the old risks while adding a new one.

For anyone writing software, two of these are directly about code: a missing length check in `fingerd` and an unpatched framework in Equifax's portal. The other two are about defaults, like hidden file extensions and trusted floppies, that made the dangerous path the easy one.

## Sources

- Brain: [History of Information entry on Brain](https://www.historyofinformation.com/detail.php?id=1676) and [Kaspersky's 1980s timeline](https://encyclopedia.kaspersky.com/knowledge/years-1980s/)
- Morris worm: [FBI case summary](https://www.fbi.gov/history/famous-cases/morris-worm) and [Harvard's excerpt from United States v. Morris](https://cyber.harvard.edu/ilaw/Cybercrime/)
- ILOVEYOU: [Microsoft's entry for Worm:VBS/LoveLetter.B](https://www.microsoft.com/en-us/wdsi/threats/malware-encyclopedia-description?Name=Worm%3AVBS%2FLoveLetter.B)
- Equifax: [Equifax's disclosure of 7 September 2017](https://investor.equifax.com/sec-filings/all-sec-filings/content/0000033185-17-000026/exhibit99120170907.htm) and the [U.S. House staff report on the breach (PDF)](https://oversight.house.gov/wp-content/uploads/2018/12/Equifax-Report.pdf)

All diagrams in this post are my own.
