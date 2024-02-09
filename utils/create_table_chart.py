from typing import List

from kerykeion import KerykeionPointModel


def create_table_chart(planets_list: List[KerykeionPointModel], first_house: KerykeionPointModel,
                 tenth_house: KerykeionPointModel):
    table = "<table>"
    table_head = ("<thead>"
                  "   <tr>"
                  "       <th>Планеты</th>"
                  "        <th>Долгота</th>"
                  "        <th>Позиция дома</th>"
                  "   </tr>"
                  "</thead>")
    table_body = "<tbody>"
    for planet in planets_list:
        table_body += ("<tr>"
                       f"   <td>{planet.name}</td>"
                       f"   <td>{planet.sign} {planet.position}</td>"
                       f"   <td>{planet.house}</td>"
                       "</tr>")
    table_body += "</tbody>"

    table_foot = (f"<tfoot>"
                  f"    <tr>"
                  f"       <td>Асцендент</td>"
                  f"       <td colspan=\"2\">{first_house.sign}</td>"
                  f"   </tr>"
                  f"    <tr>"
                  f"       <td>Середина неба</td>"
                  f"       <td colspan=\"2\">{tenth_house.sign}</td>"
                  f"   </tr>"
                  f"</tfoot>")

    table += table_head
    table += table_body
    table += table_foot
    table += "</table>"
    return table
